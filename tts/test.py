# import numpy as np
# from TTS.api import TTS
# import pyaudio
# import torch
# #nlp = spacy.load("en_core_web_sm")

# tts_model = TTS(model_name="tts_models/en/ljspeech/fast_pitch", gpu=torch.cuda.is_available())
# wav_data = tts_model.tts("Testing audio generation")
# p = pyaudio.PyAudio()
# try:
#     if isinstance(wav_data, list):
#         wav_data = np.array(wav_data, dtype=np.float32)

#     if np.abs(wav_data).max() > 0:
#         wav_data = wav_data / np.abs(wav_data).max()

#     wav_bytes = wav_data.astype(np.float32).tobytes()

#     stream = p.open(format=pyaudio.paFloat32,
#                     channels=1,
#                     rate=22050,
#                     output=True)

#     stream.write(wav_bytes)
#     stream.stop_stream()
#     stream.close()
# except Exception as e:
#     print(f"Playback error: {e}")

import torch
import time
import numpy as np
import pyaudio

# Load Silero TTS model
print("🔁 Loading model...")
model, et = torch.hub.load(repo_or_dir='snakers4/silero-models',
                       model='silero_tts',
                       language='en',
                       speaker='v3_en',
                       trust_repo=True)

print(model, et)
sample_rate = 48000  # Sampling rate for audio output

def play_audio(wav):
    """Play audio using PyAudio."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # Normalize to [-1, 1]
    wav = wav / np.abs(wav).max()
    stream.write(wav.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

# Text to speak
text = "Hello, this is Silero speaking in real-time from your CPU."

print("🔊 Generating speech...")
start_time = time.time()

# Generate waveform from text
audio = model.apply_tts(text=text,
                        speaker='en_0',
                        sample_rate=sample_rate)

end_time = time.time()

print(f"✅ Audio generated in {end_time - start_time:.2f} seconds.")
print("▶️ Playing audio...")
play_audio(audio.numpy())
print("✅ Done.")
