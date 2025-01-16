import subprocess
import os
import re
import sounddevice as sd
import scipy.io.wavfile as wav
import pyaudio
import wave
import threading
import pyttsx3

output_file = r"D:\Programming\AI\Basics\intern-assignments\Chat With Docs\streamlit_app\temp_files\output.wav"
model_path = r"D:\Programming\AI\Basics\intern-assignments\Chat With Docs\whisper.cpp\models\ggml-tiny.en-q5_0.bin"  # Path to the Whisper model
whisper_cli = r"D:\Programming\AI\Basics\intern-assignments\Chat With Docs\whisper.cpp\build\bin\Release\whisper-cli.exe" # Full path to the whisper-cli executable
output_file_audio = r"D:\Programming\AI\Basics\intern-assignments\Chat With Docs\streamlit_app\temp_files\output_audio.wav"
def text_to_audio(text):
    engine = pyttsx3.init()
    engine.save_to_file(text, output_file_audio)
    engine.runAndWait()
    print(f"Audio saved as {output_file_audio}")
    return output_file_audio

def text_to_speech(input_file):
    print(input_file)
    file_extension = input_file.split('.')[-1]
    if not file_extension.lower() == '.wav' and 0:
        command = [
            "ffmpeg", 
            "-i", input_file, 
            "-ar", "16000", 
            "-ac", "1", 
            "-c:a", "pcm_s16le", 
            output_file
        ]     

        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            print("Conversion successful!")
        else:
            return f"Error: {result.stderr}"
    command = [whisper_cli, "-m", model_path, output_file]

    # Run the command using subprocess
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        print("Transcription successful!")
        transcription_text = re.sub(r'\[.*?-->.*?\]\s*', '', result.stdout).strip()        
        return transcription_text
    else:
        return f"Error: {result.stderr}"
    
# def record_audio_old():
#     # Record for 5 seconds (adjust the duration as needed)
#     fs = 16000  # Sample rate (16 kHz)
#     duration = 2 # seconds

#     # Record audio
#     audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#     sd.wait()  # Wait for the recording to finish

#     # Define the file path to save the recording
#     file_name = "recorded_audio.wav"
#     file_path = os.path.join(save_directory, file_name)

#     # Save the audio to the specified directory
#     wav.write(file_path, fs, audio_data)

#     return file_path    

# Global stop event
stop_event = threading.Event()

# Function to record audio
def record_audio(output_file, sample_rate=16000, chunk=1024, channels=1):
    global stop_event

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open a new stream
    stream = audio.open(format=pyaudio.paInt16,  # 16-bit format
                        channels=channels,      # Mono or stereo
                        rate=sample_rate,       # Sampling rate
                        input=True,             # Input mode
                        frames_per_buffer=chunk)  # Buffer size

    # Store the audio data
    frames = []
    try:
        while not stop_event.is_set():  # Continue until the stop event is triggered
            data = stream.read(chunk)
            frames.append(data)
    except KeyboardInterrupt:
        print("Recording stopped manually.")
    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save the recorded audio as a .wav file
        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))

        print(f"Audio saved to {output_file}")

# Function to start recording in a thread
def start_recording():
    global stop_event
    stop_event.clear()
    threading.Thread(target=record_audio, args=(output_file,), daemon=True).start()

# Function to stop recording
def stop_recording():
    global stop_event
    stop_event.set()