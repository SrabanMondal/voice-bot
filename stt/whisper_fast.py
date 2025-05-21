import pyaudio
import wave
import numpy as np
import os
import time
from faster_whisper import WhisperModel
import subprocess
# Initialize Faster-Whisper model
model = WhisperModel("tiny.en", compute_type='int8', local_files_only=False)

def convert_to_whisper_format(input_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def transcribe_with_pause(text_queue):
    """
    Listen in chunks, stop on 2s silence, return transcribed text.
    """
    RATE = 44100
    CHUNK = 4096
    SILENCE_THRESHOLD = 20000000
    SILENCE_SECONDS = 2
    SILENCE_CHUNKS = 22 #int(SILENCE_SECONDS / 0.092) #22 chunks approx

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt32,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    #print("🎤 Listening...")
    frames = []
    silence_count = 0
    text = ""

    try:
        while silence_count<SILENCE_CHUNKS:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            audio_chunk = np.frombuffer(data, dtype=np.int32)
            amplitude = np.abs(audio_chunk).mean()
            #print(amplitude)
            if amplitude < SILENCE_THRESHOLD:
                silence_count += 1
            else:
                silence_count = 0

            # Save chunk to temp WAV for transcription
            
            # Stop on 2s silence
        else:
            print('silenced')
            temp_wav = "temp_chunk.wav"
            with wave.open(temp_wav, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt32))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            convert_to_whisper_format('temp_chunk.wav','temp-chunk.wav')
            processed_wav= 'temp-chunk.wav'
            # Transcribe chunk
            segments, _ = model.transcribe(processed_wav, language="en", beam_size=5)
            chunk_text = " ".join([seg.text for seg in segments]).strip()
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            if os.path.exists(processed_wav):
                os.remove(processed_wav)
            if chunk_text:
                text += chunk_text + " "
                if chunk_text.lower() == "halt" or chunk_text.lower()=='halt.' or chunk_text.startswith('halt'):
                    text = "halt"
                    
    except Exception as e:
        print(f"STT error: {e}")

    stream.stop_stream()
    stream.close()
    audio.terminate()
    if text:
        text_queue.put(text.strip())
    return text.strip() if text else None