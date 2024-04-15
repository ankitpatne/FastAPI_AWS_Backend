# Renegan

Renegan is an innovative solution developed for the Police officers, aimed at enhancing public safety through intelligent geo-tagging of privately owned cameras. This repository contains the codebase for Renegan, facilitating real-time processing of CCTV video streams, crime detection, and incident reporting.

## Tech Stack

Renegan leverages the following technologies:

- **OpenCV**: For video processing and frame analysis.
- **Boto3**: For interaction with Amazon Web Services (AWS) S3 bucket for secure storage of video footage.
- **FastAPI**: Provides a high-performance web API framework for handling HTTP requests.
- **MongoDB**: A NoSQL database used for storing camera metadata, incident details, and notifications.
- **Requests**: Used for making HTTP requests to fetch CCTV video streams and interact with external APIs.
- **MoviePy**: A Python library for video editing tasks such as concatenating video clips.
- **Python**: The primary programming language used for development.

## Features

- **Real-time Crime Detection**: Utilizes computer vision algorithms to detect criminal activities in CCTV video streams.
- **Geo-Tagging**: Precisely tags the location of privately owned cameras, facilitating efficient access to video footage during investigations.
- **Automatic Incident Reporting**: Generates real-time alerts and incident reports for law enforcement agencies and camera owners.
- **Displacement Detection**: Detects instances of camera displacement or malfunction, triggering notifications for necessary repairs.
- **Integration with AWS S3**: Securely stores CCTV footage in the cloud for easy access and retrieval.

## Setup and Configuration

To configure Renegan for your environment and run the FastAPI server, follow these steps:

1. **Clone the Repository**: Clone this repository to your local machine using Git.

2. **Install Dependencies**: Navigate to the project directory and install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

3. **Replace Placeholder URLs**: In the codebase, replace placeholder URLs, such as "YOUR_MONGODB_CONNECTION_STRING", "YOUR_S3_BUCKET_NAME", and "YOUR_S3_BUCKET_URL", with your actual MongoDB connection string and AWS S3 bucket details.

4. **Run the FastAPI Server**: Launch the FastAPI server using UVicorn with the following command:
   ```
   uvicorn main:app --reload
   ```
   This command starts the FastAPI server, reloading it automatically whenever changes are made to the codebase.

5. **Access the API**: Once the server is running, you can access the API endpoints locally by navigating to `http://localhost:8000` in your web browser or using an API testing tool like Postman.

By following these steps, you can configure and run Renegan on your local machine for testing and development purposes. Adjustments may be needed for deployment in a production environment.


For more information, please visit our complete project repo [Renegan](https://github.com/TeamRenegan/Renegan-GeoTagging-Of-Cameras.git).