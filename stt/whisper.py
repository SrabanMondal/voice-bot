import wave
import subprocess
with wave.open('temp-converted.wav','rb') as wf:
    print(wf.getsampwidth())
    print("Channels:", wf.getnchannels())
    print(wf.getnframes())
    print(wf.getframerate())
from faster_whisper import WhisperModel

model = WhisperModel("tiny.en", compute_type="int8")

segments, info = model.transcribe("temp-chunk.wav", beam_size=5)

print("Detected language:", info.language)
for segment in segments:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
