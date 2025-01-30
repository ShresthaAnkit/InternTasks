import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance as dist
import matplotlib.pyplot as plt
import ffmpeg
def get_rotation(video_path):
    """Extracts rotation metadata using ffmpeg."""
    try:
        meta = ffmpeg.probe(video_path)
        rotation = int(meta['streams'][1]['side_data_list'][0].get('rotation', 0))
        return rotation
    except:
        return 0  # No rotation metadata found
# Constants for blink detection
EAR_THRESHOLD = 0.4  # Eye aspect ratio threshold for blink detection

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils
# Landmark indices for left and right eyes
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

# Helper function to calculate eye aspect ratio (EAR)
def eye_aspect_ratio(eye_landmarks):
    # Compute the Euclidean distances between the vertical eye landmarks
    A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
    B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
    # Compute the Euclidean distance between the horizontal eye landmarks
    C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
    # Compute the eye aspect ratio
    ear = (A + B) / (C)
    return ear
path = r'C:\Users\aanki\Downloads\live_videos\0001d815c0--61f82a2956ef241fa1f94ff0.mp4'
path = r'D:\Programming\Python\AI\Basics\AMNIL Tech\Liveness Detection\lip_movement\video\fake\fake9.mp4'
# Initialize video capture
cam = cv2.VideoCapture(path)
rotation = get_rotation(path)
#rotation=0
# Variables for blink detection
blink_counter = 0  # Counter for blinks

# Initialize the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
x_data, y_data = [], []  # Lists to store frame numbers and EAR values
line, = ax.plot(x_data, y_data, 'b-',label="EAR")  # Create an empty line plot
threshold_line = ax.axhline(y=EAR_THRESHOLD, color='r', linestyle='--', label="Threshold")
ax.set_ylim(0, 0.7)  # Set y-axis limits (EAR typically ranges between 0 and 0.5)
ax.set_xlabel("Frame Number")
ax.set_ylabel("EAR")
ax.set_title("Eye Aspect Ratio (EAR) Over Time")
ax.legend()
EYE_STATUS = 0
frame_count = 0  # Counter for frame numbers
while True:
    # If the video is finished, reset it to the start
    if cam.get(cv2.CAP_PROP_POS_FRAMES) == cam.get(cv2.CAP_PROP_FRAME_COUNT):
        cam.set(cv2.CAP_PROP_POS_FRAMES, 0)

    ret, frame = cam.read()
    if not ret:
        break
    if rotation == 90:
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rotation == -90 or rotation == 270:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    # Convert the frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Face Mesh
    results = face_mesh.process(rgb_frame)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Extract landmarks for left and right eyes
            left_eye = []
            right_eye = []
            for idx in LEFT_EYE_INDICES:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                left_eye.append((x, y))
            for idx in RIGHT_EYE_INDICES:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                right_eye.append((x, y))

            # Calculate EAR for both eyes
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            EAR = (left_ear + right_ear) / 2.0
            # Update the plot data
            x_data.append(frame_count)
            y_data.append(EAR)
            frame_count += 1

            # Update the plot
            line.set_xdata(x_data)
            line.set_ydata(y_data)
            ax.relim()  # Rescale the y-axis
            ax.autoscale_view()  # Autoscale the view
            plt.draw()
            plt.pause(0.01)  # Pause to update the plot  
            # Detect blinks
            if EAR < EAR_THRESHOLD:
                EYE_STATUS = 1                    
            else:
                if EYE_STATUS == 1:
                    blink_counter += 1
                EYE_STATUS = 0   
                cv2.putText(frame, "Open", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Blink Count: {blink_counter}", (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
            mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
                )        
            
    # Display the frame
    cv2.imshow("Blink Detection", frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()