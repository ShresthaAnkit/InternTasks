import librosa
import numpy as np

def get_audio_energy(video_path,fps):
    # Load audio using librosa
    y, sr = librosa.load(video_path, sr=16000, mono=True)        
    
    # Calculate hop_length and frame_length to match video frames
    hop_length = int(sr / fps)  # Hop length to match video frame rate
    frame_length = int(sr * 0.05)  # 50ms window (can be adjusted)
    
    # Calculate short-time energy
    energy = np.array([
        sum(abs(y[i:i+frame_length])**2)
        for i in range(0, len(y), hop_length)
    ])
    
    return energy

