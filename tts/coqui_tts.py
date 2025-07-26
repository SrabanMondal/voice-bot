import threading
import queue
import numpy as np
import pyaudio
import torch
from TTS.api import TTS
import time
# Load TTS model once (CPU or GPU based on availability)
tts_model = TTS(model_name="tts_models/en/ljspeech/fast_pitch", gpu=torch.cuda.is_available())
print("✅ TTS Model Loaded")

def tts_worker(worker_id, stop_event, sentence_queue, audio_queue):
    while not stop_event.is_set():
        try:
            item = sentence_queue.get(timeout=1)
        except queue.Empty:
            continue

        if item is None:
            print(f"[Worker {worker_id}] stopping")
            audio_queue.put((float('inf'), None))
            break

        idx, sentence = item
        print(f"[Worker {worker_id}] Processing: {sentence}")
        
        try:
            start = time.time()
            wav = tts_model.tts(sentence.strip())  # List[float] output
            end = time.time()
            print(f"Time taken by worker {worker_id} for processing {sentence.strip()}: {end-start}")
            audio_queue.put((idx, wav))
            print(f"[Worker {worker_id}] Done")
        except Exception as e:
            print(f"[Worker {worker_id}] Error: {e}")

def playback_worker(stop_event, audio_queue):
    p = pyaudio.PyAudio()
    next_index = 0
    buffer = {}
    finished_workers = 0

    while not stop_event.is_set():
        # Check if next audio is already in buffer
        if next_index in buffer:
            wav_data = buffer.pop(next_index)
        else:
            try:
                idx, wav_data = audio_queue.get(timeout=1)
                if wav_data is None:
                    finished_workers += 1
                    if finished_workers == 2:
                        print("✅ All workers finished")
                        break
                    continue
                buffer[idx] = wav_data
                continue
            except queue.Empty:
                continue

        print(f"🔊 Playing sentence {next_index}")
        try:
            # Convert list to NumPy array
            if isinstance(wav_data, list):
                wav_data = np.array(wav_data, dtype=np.float32)

            # Normalize audio volume
            if np.abs(wav_data).max() > 0:
                wav_data = wav_data / np.abs(wav_data).max()

            wav_bytes = wav_data.astype(np.float32).tobytes()

            # Play with PyAudio
            stream = p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=22050,
                            output=True)
            stream.write(wav_bytes)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"Playback error: {e}")

        next_index += 1

    p.terminate()

def speak_text(sentence_queue, stop_event=None):
    audio_queue = queue.PriorityQueue()
    print("🚀 Starting TTS + Playback Threads")

    producers = [threading.Thread(target=tts_worker, args=(i, stop_event, sentence_queue, audio_queue)) for i in range(2)]
    for p in producers:
        p.start()

    playback = threading.Thread(target=playback_worker, args=(stop_event, audio_queue))
    playback.start()

    for p in producers:
        p.join()
    playback.join()

    print("✅ Done speaking")
