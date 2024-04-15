import cv2
import boto3 
from fastapi import FastAPI
from contextlib import asynccontextmanager
import time
from moviepy.editor import concatenate_videoclips, VideoFileClip
from crime_detection import detect_crime
from datetime import datetime
from displacement_detection import detect_cctv_fall
import random
from pymongo import MongoClient
import requests
import numpy
import requests
from PIL import Image
from io import BytesIO


# Replace with your camera's RTSP URL
VIDEO_PATH = 0
VIDEO_URL = "http://192.168.24.223:8081/out.jpg?q=30&id=0.06486201992911766"

# sample rtsp url with password and username
# VIDEO_PATH = "rtsp://username:password@ip_address:port_number"

# NO_OF_FRAMES_PER_SECOND = 4


# MongoDB connection
client = MongoClient(
    "YOUR_MONGODB_CONNECTION_STRING"
)
db = client["YOUR_DATABASE_NAME"]


# Dictionary to store the first frame of each hour which will be used for displacement detection
first_frames = {}


def trim_video(frames, start_time, end_time):
    # Filter frames between start_time and end_time
    frames_to_include = [
        frame
        for frame, timestamp in frames
        if start_time - 5 <= timestamp <= end_time + 5
    ]

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("trimmed.mp4", fourcc, cap.get(cv2.CAP_PROP_FPS), (640, 480))

    for frame in frames_to_include:
        # Write the frame to the video file
        out.write(frame)

    # Release the VideoWriter
    out.release()

    # Return the path to the trimmed video
    return "trimmed.mp4"


def generate_report(event_details):
    db["incident_notification"].insert_one(event_details)
    # make a get request to the API endpoint
    requests.post(
        "https://renegan-inc-backend.onrender.com/videos/sendmail"
    )


def save_frames_as_video(frames):
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(
        "output_att1.mp4", fourcc, cap.get(cv2.CAP_PROP_FPS), (640, 480)
    )

    for frame, _ in frames:
        # Write the frame to the video file
        out.write(frame)

    # Release the VideoWriter
    out.release()

    # Return the path to the video file
    return "output_att1.mp4"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global cap
    cap = cv2.VideoCapture(VIDEO_PATH)
    # Capture the frames from the url with given epoch time

    global local_frame
    response = requests.get(VIDEO_URL)
    image_frame = Image.open(BytesIO(response.content))
    # Convert image to MatLike
    local_frame = cv2.cvtColor(numpy.array(image_frame), cv2.COLOR_RGB2BGR)
    yield
    cap.release()

def cap_frame():
    response = requests.get(VIDEO_URL)
    image_frame = Image.open(BytesIO(response.content))
    # Convert image to MatLike
    return cv2.cvtColor(numpy.array(image_frame), cv2.COLOR_RGB2BGR)

app = FastAPI(lifespan=lifespan)

crime_scene_urls = []



@app.get("/process_stream")
async def process_stream():
    frame_count = 0
    start_time = None
    frames = []
    crime_scenes = []
    crime_detected = False
    crime_end_time = None
    last_upload_time = time.time()
    crime_start_time = time.time()
    s3_client = boto3.client("s3")
    frame_count_after_crime = 0
    is_crime_detected = False
    last_state_of_displacement = None
    # rr, ff = cap.read()
    crime_weapon = None
    camera_displaced = False
    cam_disp_count = 0
    cam_not_disp_count = 0
    real_cam_disp_count = 0
    cam_disp_time = None

    while True:
        # ret, frame = cap.read()
        frame = cap_frame()
        frame_count += 1

        # cv2.imshow('frame_count', frame)
        # print(frame)

        # if frame_count % 2 == 0:
        # if not ret:
        #     print("Error reading frame from stream")
        #     break

        current_time = time.time()
        frames.append((frame, current_time))

        ##########################################################
        ####### Alternative approach to detect crime scenes #######

        # current_hour = datetime.now().hour

        # # If this is the first frame of the current hour
        # if current_hour not in first_frames:
        #     # Store the frame
        #     first_frames[current_hour] = frame

        # else:

        #     # check for displacement
        #     if detect_cctv_fall(first_frames[current_hour], frame):
        #         # The frames differ, add an object to MongoDB
        #         collection.insert_one({"hour": current_hour, "timestamp": current_time})

        ###########################################################

        if detect_cctv_fall(frames[0][0], frame):
            # The frames differ
            cam_disp_time = (
                min(cam_disp_time, current_time)
                if cam_disp_time is not None
                else current_time
            )
            current_state = 1
            cam_disp_count += 1
            print("CAM displaced")

            # Save the current frame as an image with date time stamp
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # cv2.imwrite(f"displaced_images/displaced_{date_str}.jpg", frame)
        else:
            # The frames do not differ
            current_state = 0
            cam_not_disp_count += 1
            print("CAM not displaced")

        # If the state has changed
        if (
            last_state_of_displacement is not None
            and current_state != last_state_of_displacement
        ):
            real_cam_disp_count += 1

        # Update the last state
        last_state_of_displacement = current_state

        # Check if an hour has passed since the last upload
        if current_time >= last_upload_time + 60 * 60:
            # An hour has passed, save the current frames as a video and upload to S3
            video_file = save_frames_as_video(frames)
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            s3_client.upload_file(
                video_file, "YOUR_S3_BUCKET_NAME", f"complete_footage/{date_str}.mp4"
            )
            # s3_complete_footage_url = f"https://YOUR_S3_BUCKET_NAME.s3.ap-south-1.amazonaws.com/complete_footage/{date_str}.mp4"
            last_upload_time = current_time
            # upload to mongoDB
            # db["complete_footage"].insert_one({"timestamp": current_time, "url": s3_complete_footage_url, "cameraId": "123456",})

        if detect_crime(frame):
            if not crime_detected:
                crime_detected = True
                crime_start_time = current_time
                crime_weapon = detect_crime(frame)

        elif crime_detected and crime_end_time is None:
            crime_end_time = current_time

        if crime_detected and crime_end_time is not None:
            # Crime detected, trim video and upload to the second S3 bucket
            event_details = {
                # random cam ID
                "cameraId": random.randint(1, 100000),
                "crime_weapon": crime_weapon,  # Add the weapon information to the event details
                "start_time": crime_start_time,
                "end_time": crime_end_time,
            }
            start_time = crime_start_time - 3
            end_time = crime_end_time + 3
            crime_scenes.append([start_time, end_time])

            ##########################################################
            ######### ALTERNATIVE APPROACH #########
            # trimmed_video = trim_video(frames, start_time, end_time)
            # timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            # video_filename = f"Dhishkyau_Cam_crime_video_{timestamp_str}.mp4"
            # s3_client.upload_file(trimmed_video, "ankit-s3-1", f"rene_2/{video_filename}")

            # is_crime_detected = True
            # frame_count_after_crime = 0
            # frame_count_after_crime += 1
            ##########################################################
            
            generate_report(event_details)

            crime_detected = False
            crime_end_time = None
            crime_start_time = time.time()
        
        #######################################################################
            ##### APPROACH NO. 2 --- BEGIN #####

            # if frame_count_after_crime >= 100:
            #     s3_client.upload_file(trimmed_video, "ankit-s3-1", f"rene_2/{video_filename}")
            #     break
        # if is_crime_detected:
        #     frame_count_after_crime += 1

        # if frame_count_after_crime >= 200:
        #   start_time = crime_scenes[0][0]
        #     trimmed_video = trim_video(frames, start_time, current_time)
        # delete the frames from start_time to current_time-3 (so that other video can have a start of 3 secs too) from frames
        #
        #     timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     video_filename = f"Hinata_Cam_crime_video_{timestamp_str}.mp4"
        #     s3_client.upload_file(trimmed_video, "ankit-s3-1", f"rene_2/{video_filename}")
        # Generate a report
        # event_details = {
        #     "crime_weapon": crime_weapon,  # Add the weapon information to the event details
        #     "start_time": crime_start_time,
        #     "end_time": current_time,
        # }
        # generate_report(event_details)
        # delete the frames from start_time to current_time-3 (so that other video can have a start of 3 secs too) from crime_scenes

        #     is_crime_detected = False
        #     frame_count_after_crime = 0

        # Remove frames that are more than 5 minutes old
        # while frames and frames[0][1] < current_time - 5 * 60:
        #     frames.pop(0)
        # exit the loop automatically after 10 secs

        #### APPROACH NO. 2 --- END #####
        #######################################################################

        if frame_count >= 500:  ### For testing purposes only. Break the loop after 500 frames ###
            # if is_crime_detected:
            #     trimmed_video = trim_video(frames, start_time, current_time)
            #     timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            #     video_filename = f"Hinata_Cam_crime_video_{timestamp_str}.mp4"
            #     s3_client.upload_file(trimmed_video, "ankit-s3-1", f"rene_2/{video_filename}")
            break
    i = 0
    while i < len(crime_scenes) - 1:
        # If the end time of the current video and the start time of the next video are less than or equal to 3 seconds apart
        if crime_scenes[i + 1][0] <= crime_scenes[i][1]:
            # Merge the two videos by setting the end time of the current video to the end time of the next video
            crime_scenes[i][1] = crime_scenes[i + 1][1]
            # Remove the next video from the list
            del crime_scenes[i + 1]
        else:
            i += 1

    for i in range(len(crime_scenes)):
        trimmed_video = trim_video(frames, crime_scenes[i][0], crime_scenes[i][1])
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"crime_scenes/crime_scene_{timestamp_str}.mp4"
        s3_client.upload_file(trimmed_video, "ankit-s3-1", video_filename)
        s3_crime_scene_url = f"YOUR_S3_BUCKET_URL/crime_scenes/crime_scene_{video_filename}"
        crime_scene_urls.append(s3_crime_scene_url)

    # if camera_displaced:
    print("CAM displaced", cam_disp_count)
    # else:
    print("CAM not displaced", cam_not_disp_count)

    if cam_disp_count > cam_not_disp_count:
        print(f"Camera is displaced for {real_cam_disp_count} times.")
        db["displacement_notification"].insert_one(
            {
                "timestamp": cam_disp_time,
                "cameraId": "123456", # random cam ID for testing
            }
        )

    return "Stream processing complete"


# New API endpoint to get all crime scene URLs
@app.get("/crime-scenes")
def get_crime_scenes():
    return {"crime_scenes": crime_scene_urls}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)