import threading
import queue
import os
import pyaudio
import wave
#import spacy
from TTS.api import TTS
import tempfile
import torch
#nlp = spacy.load("en_core_web_sm")

tts_model = TTS(model_name="tts_models/en/ljspeech/fast_pitch", gpu=torch.cuda.is_available())
#tts_model2 = TTS(model_name="tts_models/en/ljspeech/vits", gpu=False)
print("tts loaded")
def tts_worker(worker_id, stop_event, sentence_queue, audio_queue):
    
    while not stop_event.is_set():
        item = sentence_queue.get()
        if item is None:
            print(f"[Worker {worker_id}] stopped")
            audio_queue.put((float('inf'), None))
            break
        idx, sentence = item
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            tmp_path = tmp_wav.name
            print(f"[Worker {worker_id}] Processing:", sentence)
            try:
                tts_model.tts_to_file(text=sentence.strip(), file_path=tmp_path)
                # if(worker_id==0):
                # else:
                #     tts_model2.tts_to_file(text=sentence.strip(), file_path=tmp_path, emotion='Happy')
                print(f"[Worker {worker_id}] Done")
                audio_queue.put((idx, tmp_path))
            except Exception as e:
                print(f"[Worker {worker_id}] Failed: {e}")
def playback_worker(stop_event, audio_queue):
    p = pyaudio.PyAudio()
    next_index = 0
    buffer = {}
    counter=0
    while not stop_event.is_set():
        if next_index in buffer:
                wav_path = buffer.pop(next_index)
        else:
            try:
                item = audio_queue.get()
                if item[1] is None:
                    print("one worked ended")
                    counter+=1
                    if(counter==2):
                        print("No more audio-- ending")
                        break
                    else:
                        continue
                idx, wav_path = item
                #if idx != next_index:
                print("Audio added to buffer: ",idx)
                buffer[idx] = wav_path
                continue
            except queue.Empty:
                continue
        print("Audio processing: ",next_index)
        try:
            wf = wave.open(wav_path, 'rb')
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            chunk = 1024
            data = wf.readframes(chunk)
            while data and not stop_event.is_set():
                stream.write(data)
                data = wf.readframes(chunk)
            stream.stop_stream()
            stream.close()
            wf.close()
        finally:
            os.remove(wav_path)
        next_index += 1
    p.terminate()
        
def speak_text_multi(sentence_queue, stop_event=None):
    #global tts_model
    audio_queue = queue.PriorityQueue()
    print("Initializing producers and playback")
    producers = [threading.Thread(target=tts_worker, args=(i,stop_event,sentence_queue,audio_queue)) for i in range(2)]
    for p in producers:
        p.start()
    playback = threading.Thread(target=playback_worker, args=(stop_event,audio_queue))
    playback.start()
    for p in producers:
        p.join()
    playback.join()
    print("Speaking done")
    #stop_event.set()
    #print("Whisper Wake")