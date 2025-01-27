import cv2
import librosa
import mediapipe as mp
import numpy as np
from scipy.signal import resample
from sklearn.preprocessing import StandardScaler
from scipy.linalg import svd
from moviepy import VideoFileClip
import subprocess
import os

# Step 1: Load Video and Extract Audio
def extract_audio_from_video(video_path, audio_path=r"D:\Programming\Python\AI\Basics\intern-phase-2\Liveness Detection\lip_movement\audio"):
    # Extract video name (without extension)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    # Define the audio file name with the same base name as the video
    audio_path = os.path.join(audio_path, f"{video_name}.wav")
    # Check if the audio file already exists
    if os.path.exists(audio_path):
        print(f"Audio file already exists: {audio_path}")
        return audio_path
    command = [
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return audio_path

# Step 2: Extract Audio Features
def extract_audio_features(audio_path):
    """Extracts MFCC features from the audio."""
    y, sr = librosa.load(audio_path, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # Shape: (13, n_frames)
    return mfccs.T  # Transpose to have frames along rows

# Step 3: Extract Lip Movement Features
def extract_lip_features(video_path):
    """Extracts lip landmarks from the video using MediaPipe."""
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)
    cap = cv2.VideoCapture(video_path)
    
    lip_features = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:
                # Extract lip landmarks (e.g., indices 0-16)
                lips = [(lm.x, lm.y) for i, lm in enumerate(landmarks.landmark) if i in range(0, 17)]
                lip_features.append(np.array(lips).flatten())
    cap.release()
    return np.array(lip_features)

# Step 4: Align and Normalize Features
def align_and_normalize_features(audio_features, video_features):
    """Aligns audio and video features by resampling and normalizing."""
    n_video_frames = video_features.shape[0]
    aligned_audio_features = resample(audio_features, n_video_frames)
    
    scaler = StandardScaler()
    aligned_audio_features = scaler.fit_transform(aligned_audio_features)
    video_features = scaler.fit_transform(video_features)
    return aligned_audio_features, video_features

# Step 5: Perform Co-Inertia Analysis
def perform_coia(audio_features, video_features):
    """Performs Co-Inertia Analysis and returns the co-inertia score."""
    cross_covariance = np.dot(audio_features.T, video_features)
    _, singular_values, _ = svd(cross_covariance)
    co_inertia_score = np.sum(singular_values)
    return co_inertia_score
def calculate_L(p_hat, D):
    """
    Calculates the value of L based on the given equation.

    Args:
        p_hat: A numpy array representing the estimated probability values.
        D: The value of D for the calculation.

    Returns:
        The calculated value of L.
    """

    # Calculate p_ref
    p_ref = np.max(p_hat)

    # Calculate f(p_hat, i)
    f_p_hat = np.where(p_hat <= p_ref, 1, 0)

    # Calculate the sum of f(p_hat, i)
    sum_f_p_hat = np.sum(f_p_hat)

    # Calculate mean(p_hat)
    mean_p_hat = np.mean(p_hat)

    # Calculate L
    L = (sum_f_p_hat / (2 * D + 1)) * ((p_ref / mean_p_hat) - 1)

    return L

# Step 6: Main Function for Liveness Detection
def detect_liveness(video_path, threshold=0.5):
    """Main function to detect liveness using COIA."""
    # Extract audio from video
    print("[INFO] Extracting audio...")
    audio_path = extract_audio_from_video(video_path)
    
    # Extract audio features
    print("[INFO] Extracting audio features...")
    audio_features = extract_audio_features(audio_path)
    
    # Extract lip movement features
    print("[INFO] Extracting lip movement features...")
    lip_features = extract_lip_features(video_path)
    
    # Align and normalize features
    print("[INFO] Aligning and normalizing features...")
    aligned_audio, aligned_video = align_and_normalize_features(audio_features, lip_features)
    
    # Perform Co-Inertia Analysis
    print("[INFO] Performing Co-Inertia Analysis...")
    co_inertia_score = perform_coia(aligned_audio, aligned_video)
    print(f"[INFO] Co-Inertia Score: {co_inertia_score}")
    L = calculate_L(co_inertia_score,10)
    print(f"[INFO] Threshold: {L}")
    
    # Classify based on the threshold
    if L > threshold:
        print("[RESULT] Live (Synchronized)")
    else:
        print("[RESULT] Fake (Desynchronized)")

# Example Usage
video_path = r"D:\Programming\Python\AI\Basics\intern-phase-2\Liveness Detection\lip_movement\video\fake3.mp4"
detect_liveness(video_path)
