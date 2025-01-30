import numpy as np
from scipy.stats import spearmanr
import warnings
from scipy.signal import find_peaks
from audio_processes import get_audio_energy
from video_processes import extract_video_features

# Constants
START_DELAY = 10
WINDOW_SIZE = 9
# Min-max normalization function
def min_max_normalize(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))
def moving_average(data, window_size):
    # Ensure the window size is odd
    if window_size % 2 == 0:
        raise ValueError("Window size must be odd to maintain symmetry.")
    
    # Create a window of ones and normalize it
    window = np.ones(window_size) / window_size
    
    # Pad the data to handle edges
    pad_size = window_size // 2
    padded_data = np.pad(data, (pad_size, pad_size), mode='edge')  # Reflect padding
    
    # Apply convolution to compute the moving average
    smoothed_data = np.convolve(padded_data, window, mode='valid')
    
    return smoothed_data

def detect_peaks(data):
    # Compute absolute difference between consecutive frames
    movement = np.abs(np.diff(data))
    peaks, _ = find_peaks(movement, height=np.mean(movement) + np.std(movement),
                      prominence=0.05, width=1, distance=2)
    return peaks  

def detect_liveness(video_path):
    """
    Detects liveness in a given video path.

    Parameters
    ----------
    video_path : str
        Path to the video file.

    Returns
    -------
    pred : str
        'REAL' or 'FAKE' depending on liveness detection result.

    Notes
    -----
    The method uses audio-video correlation to detect liveness. It extracts the
    audio energy and lip features from the video, computes the correlation between
    the two, and uses it to decide whether the video is real or fake. Additional
    heuristics are used to filter out fake videos with low audio energy and few
    blinks.
    """

    lip_feat,blink_count,speak_count,fps = extract_video_features(video_path)
    audio_energy = get_audio_energy(video_path,fps)
    mean_dist = np.mean(lip_feat,axis=1)
    min_len = min(len(mean_dist),len(audio_energy))
    normalized_dist = min_max_normalize(mean_dist)[START_DELAY:min_len]
    normalized_audio = min_max_normalize(audio_energy)[START_DELAY:min_len]

    audio_changes = len(detect_peaks(audio_energy))

    correlation, _ = spearmanr(normalized_dist, normalized_audio)                 
    if not (speak_count>=2 and audio_changes>=2):    
        pred = 'FAKE'
    else:
        if correlation < 0: 
            if correlation > -0.1 and blink_count>0:
                pred = 'REAL'
            else:
                pred = 'FAKE'
        else:
            pred = 'REAL'            
    return pred