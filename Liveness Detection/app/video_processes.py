import cv2
import mediapipe as mp
import math
from scipy.spatial import distance as dist

# Calculate the Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye_landmarks):
    # Compute the Euclidean distances between the vertical eye landmarks
    """
    Computes the Eye Aspect Ratio (EAR) from a set of facial landmarks
    corresponding to an eye.

    The EAR is a measure of how open or closed an eye is.

    Parameters
    ----------
    eye_landmarks : list
        A list of 6 (x, y)-coordinates corresponding to the 6 facial landmarks
        defining an eye. The order of the landmarks is as follows:

        0. Left corner of the eye
        1. Top left position of the eye
        2. Top right position of the eye
        3. Right corner of the eye
        4. Bottom right position of the eye 
        5. Bottom left position of the eye

    Returns
    -------
    ear : float
        The Eye Aspect Ratio (EAR) of the given eye. The EAR is a measure of
        how open or closed the eye is. Larger values indicate that the eye is
        more open, while smaller values indicate that the eye is more closed.
    """

    A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
    B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
    # Compute the Euclidean distance between the horizontal eye landmarks
    C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
    # Compute the eye aspect ratio
    ear = (A + B) / (C)
    return ear
# Calculate the Mouth Aspect Ratio (MAR)
def mouth_aspect_ratio(mouth_landmarks):    
    """
    Computes the Mouth Aspect Ratio (MAR) from a set of facial landmarks
    corresponding to the mouth.

    The MAR is a measure of how open or closed the mouth is.

    Parameters
    ----------
    mouth_landmarks : iterable of 2-tuples
        An iterable of (x, y) coordinates of the facial landmarks
        corresponding to the mouth.

    Returns
    -------
    float
        The Mouth Aspect Ratio (MAR) of the facial landmarks.

    Notes
    -----
    The MAR is computed as the ratio of the sum of the Euclidean distances
    between the vertical landmarks to the Euclidean distance between the
    horizontal landmarks.

    """
    A = dist.euclidean(mouth_landmarks[1], mouth_landmarks[5])
    B = dist.euclidean(mouth_landmarks[2], mouth_landmarks[4])
    # Compute the Euclidean distance between the horizontal eye landmarks
    C = dist.euclidean(mouth_landmarks[0], mouth_landmarks[3])
    # Compute the eye aspect ratio
    mar = (A + B) / (C)
    return mar
def extract_video_features(video_path):    
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)    
    cap = cv2.VideoCapture(video_path)    
    # Get video frame rate using OpenCV    
    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second    

    MOUTH_OPEN = 0 # OPEN = 0 and CLOSED = 1
    speak_count = 0 # Total number of mouth open and close detected    

    # Landmark indices for upper and lower lips
    upper_lip_points = [185,40,39,37,0,267,269,270,409]
    lower_lip_points = [146,91,181,84,17,314,405,321,375]    
    MOUTH_INDICES = [185,37,267,409,314,84]
    MAR_THRESHOLD = 1.25
    # Variables for blink detection
    EYE_STATUS = 0  # OPEN = 0 and CLOSED = 1
    blink_count = 0  # Total number of blinks detected
    EAR = 0
    EAR_THRESHOLD = 0.4  # Eye aspect ratio threshold for blink detection    
    # Landmark indices for left and right eyes
    LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
    lip_features = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:                           
                # face_width = math.sqrt((landmarks.landmark[323].x - landmarks.landmark[93].x)**2 + (landmarks.landmark[323].y - landmarks.landmark[93].y)**2)
                
                # Lip movement feature extraction
                upper_lips = [(lm.x, lm.y) for i, lm in enumerate(landmarks.landmark) if i in upper_lip_points]
                lower_lips = [(lm.x, lm.y) for i, lm in enumerate(landmarks.landmark) if i in lower_lip_points]
                distances = [math.sqrt((ul[0] - ll[0])**2 + (ul[1] - ll[1])**2) for ul, ll in zip(upper_lips, lower_lips)]                            
                mouth = []
                for idx in MOUTH_INDICES:
                    landmark = landmarks.landmark[idx]
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    mouth.append((x, y))
                MAR = mouth_aspect_ratio(mouth)
                lip_features.append(distances)
                if MAR > MAR_THRESHOLD:                
                    MOUTH_OPEN = 1
                else:
                    if MOUTH_OPEN == 1:
                        speak_count += 1
                    MOUTH_OPEN = 0
                
                # Eye movement feature extraction                
                # Extract landmarks for left and right eyes
                left_eye = []
                right_eye = []
                for idx in LEFT_EYE_INDICES:
                    landmark = landmarks.landmark[idx]
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    left_eye.append((x, y))
                for idx in RIGHT_EYE_INDICES:
                    landmark = landmarks.landmark[idx]
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    right_eye.append((x, y))

                # Calculate EAR for both eyes
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                EAR = (left_ear + right_ear) / 2.0
                
                if EAR < EAR_THRESHOLD:
                    EYE_STATUS = 1                    
                else:
                    if EYE_STATUS == 1:
                        blink_count += 1
                    EYE_STATUS = 0                    
    cap.release()
    return lip_features,blink_count,speak_count, fps