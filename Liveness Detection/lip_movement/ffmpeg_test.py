import subprocess

def extract_audio_from_video(video_path, audio_path):
    command = [
        'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return audio_path

extract_audio_from_video(
    video_path=r"D:\Programming\Python\AI\Basics\intern-phase-2\Liveness Detection\lip_movement\video_demo.mp4",
    audio_path=r"D:\Programming\Python\AI\Basics\intern-phase-2\Liveness Detection\lip_movement\extracted_audio.wav"    
)