import os

from ultralytics import YOLO
import cv2


# VIDEOS_DIR = os.path.join('.', 'videos')

# video_path = os.path.join('attack.mp4')
# video_path_out = '{}_out.mp4'.format(video_path.split('.')[0])

# cap = cv2.VideoCapture(video_path)
# ret, frame = cap.read()
# H, W, _ = frame.shape
# out = cv2.VideoWriter(video_path_out, cv2.VideoWriter_fourcc(*'MP4V'), int(cap.get(cv2.CAP_PROP_FPS)), (W, H))

# model_path = 'best.pt'

# # Load a model
# model = YOLO(model_path)  # load a custom model

# threshold = 0.5
# flag = 0
# sets = {}
# frame_count = 0
# while ret:
#     frame_count += 1
#     results = model(frame)[0]

#     for result in results.boxes.data.tolist():
#         x1, y1, x2, y2, score, class_id = result

        


#         if score > threshold:
#             sets[frame_count] = results.names[int(class_id)].upper()
#             cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
#             cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
            
#             flag = 1

#     out.write(frame)
#     ret, frame = cap.read()

# cap.release()
# out.release()
# cv2.destroyAllWindows()
# print(flag)

# export sets to csv
# import csv

# with open('sets.csv', 'w') as f:
#     for key in sets.keys():
#         f.write("%s,%s\n"%(key,sets[key]))

# function to detect crime 




# from ultralytics import YOLO
# import cv2


model_path = 'best.pt'

# Load a model
model = YOLO(model_path)  # load a custom model

threshold = 0.5

cnt = 0

def detect_crime(frame):
    results = model(frame)[0]
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        if score > threshold:
            return results.names[int(class_id)].upper()
    return False


#     global cnt
#     if cnt > 650:
#         return True
#     cnt += 1
#     return False

