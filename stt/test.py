import pyaudio
import numpy as np
import wave
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt24,
    channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=4096
)
frames =[]
print("recording..")
import time 
time.sleep(2)
print("START")
for i in range(0,int(44100/4096*5)):
    data = stream.read(4096)
    frames.append(data)
temp_wav = "temp_chunk.wav"
with wave.open(temp_wav, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt24))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
stream.stop_stream()
stream.close()
p.terminate()
