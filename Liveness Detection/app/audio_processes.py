import librosa
import numpy as np
from moviepy import VideoFileClip
import tempfile

def extract_audio_from_video(video_path):
    video_clip = VideoFileClip(video_path)
    audio = video_clip.audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio.write_audiofile(temp_audio.name)
        return temp_audio.name

def get_audio_energy(video_path,fps):
    audio_path = extract_audio_from_video(video_path)
    # Load audio using librosa
    y, sr = librosa.load(audio_path, sr=16000, mono=True)            
    # Calculate hop_length and frame_length to match video frames
    hop_length = int(sr / fps)  # Hop length to match video frame rate
    frame_length = int(sr * 0.05)  # 50ms window (can be adjusted)
    
    # Calculate short-time energy
    energy = np.array([
        sum(abs(y[i:i+frame_length])**2)
        for i in range(0, len(y), hop_length)
    ])
    
    return energy

