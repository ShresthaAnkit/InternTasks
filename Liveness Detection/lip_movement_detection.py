import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance as dist
import matplotlib.pyplot as plt
import math
import subprocess
import ffmpeg

def get_rotation(video_path):
    """Extracts rotation metadata using ffmpeg."""
    try:
        meta = ffmpeg.probe(video_path)
        rotation = int(meta['streams'][1]['side_data_list'][0].get('rotation', 0))
        return rotation
    except:
        return 0  # No rotation metadata found
def aspect_ratio(mouth_landmarks):
    # Compute the Euclidean distances between the vertical eye landmarks
    A = dist.euclidean(mouth_landmarks[1], mouth_landmarks[5])
    B = dist.euclidean(mouth_landmarks[2], mouth_landmarks[4])
    # Compute the Euclidean distance between the horizontal eye landmarks
    C = dist.euclidean(mouth_landmarks[0], mouth_landmarks[3])
    # Compute the eye aspect ratio
    ear = (A + B) / (C)
    return ear
# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils
# Landmark indices for left and right eyes
# upper_lip_points = [185,40,39,37,0,267,269,270,409]
# lower_lip_points = [146,91,181,84,17,314,405,321,375]   
MOUTH_INDICES = [185,37,267,409,314,84]

path = r'D:\Programming\Python\AI\Basics\AMNIL Tech\Liveness Detection\lip_movement\video\real\real1.mp4'
# Initialize video capture
cam = cv2.VideoCapture(0)
rotation = get_rotation(path)
rotation=0
print('Rotation:',rotation)
# Initialize the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
THRESHOLD = 1.25
threshold_line = ax.axhline(y=THRESHOLD, color='r', linestyle='--', label="Threshold")
x_data, y_data = [], []  # Lists to store frame numbers and EAR values
line, = ax.plot(x_data, y_data, 'b-',label="Mouth Aspect Ratio (MAR)")  # Create an empty line plot
#threshold_line = ax.axhline(y=EAR_THRESHOLD, color='r', linestyle='--', label="Threshold")
#ax.set_ylim(0, 0.7)  # Set y-axis limits (EAR typically ranges between 0 and 0.5)
ax.set_xlabel("Frame Number")
ax.set_ylabel("Mouth Aspect Ratio (MAR)")
ax.set_title("Mouth Aspect Ratio Over Time")
ax.legend()
speak_count = 0
MOUTH_OPEN = 0
MAR = 0
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
    lip_features = []
    # Process the frame with MediaPipe Face Mesh
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            #face_width = math.sqrt((landmarks.landmark[323].x - landmarks.landmark[93].x)**2 + (landmarks.landmark[323].y - landmarks.landmark[93].y)**2)
            #lip_width = math.sqrt((landmarks.landmark[61].x - landmarks.landmark[409].x)**2 + (landmarks.landmark[61].y - landmarks.landmark[409].y)**2) * 9
            # Lip movement feature extraction
            # upper_lips = [(lm.x, lm.y) for i, lm in enumerate(landmarks.landmark) if i in upper_lip_points]
            # lower_lips = [(lm.x, lm.y) for i, lm in enumerate(landmarks.landmark) if i in lower_lip_points]
            #distances = [math.sqrt((ul[0]/lip_width - ll[0]/lip_width)**2 + (ul[1]/lip_width - ll[1]/lip_width)**2) for ul, ll in zip(upper_lips, lower_lips)]                            
            mouth = []
            for idx in MOUTH_INDICES:
                landmark = landmarks.landmark[idx]
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                mouth.append((x, y))
            MAR = aspect_ratio(mouth)
            #lip_features.append(MAR)  # Append the list of distances for each frame to lip_features

            # Update the plot data
            x_data.append(frame_count)
            y_data.append(MAR)            
            frame_count += 1            
            # Update the plot
            line.set_xdata(x_data)
            line.set_ydata(y_data)
            ax.relim()  # Rescale the y-axis
            ax.autoscale_view()  # Autoscale the view
            plt.draw()
            plt.pause(0.01)  # Pause to update the plot  
            if MAR > THRESHOLD:                
                MOUTH_OPEN = 1
            else:
                if MOUTH_OPEN == 1:
                    speak_count += 1
                MOUTH_OPEN = 0
                cv2.putText(frame, "Open", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Speak Count: {speak_count}", (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=landmarks,
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