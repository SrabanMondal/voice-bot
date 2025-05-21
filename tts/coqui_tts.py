import threading
import queue
import re
import os
import pyaudio
import wave
import spacy
from TTS.api import TTS
import tempfile
#nlp = spacy.load("en_core_web_sm")
# Init model once globally (can move this out to init)
print('loading tts')
tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True, gpu=False)
print('loaded')
def speak_text_stream(text, stop_event=None):
    """
    Stream text-to-speech using PyAudio with producer-consumer threading model.
    Text is split into sentences for smoother TTS + playback flow.
    """
    if stop_event and stop_event.is_set():
        return
    print("tts text: ",text)
    # 🧠 Step 1: Sentence Tokenization (use spaCy later for smarter chunks)
    #doc = nlp(text)
    
    words= text.split(' ')
    sentences = [' '.join(words[i:i+4]) for i in range(0,len(words),4)]
    if not sentences:
        return

    # 📦 Create audio queue
    audio_queue = queue.Queue()

    # 🧵 TTS producer thread
    def tts_worker():
        for sentence in sentences:
            if stop_event and stop_event.is_set():
                break

            # Use tempfile to hold generated WAV
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                tmp_path = tmp_wav.name
                print("Speech chunk processing: ",sentence)
                tts_model.tts_to_file(text=sentence, file_path=tmp_path, language='hi')
                print("speech chunk processed")
            audio_queue.put(tmp_path)

        # Signal end of TTS
        audio_queue.put(None)

    # 🧵 PyAudio consumer thread
    def playback_worker():
        p = pyaudio.PyAudio()
        while not stop_event.is_set():
            wav_path = audio_queue.get()
            if wav_path is None:
                break

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

        p.terminate()

    # Start both threads
    tts_thread = threading.Thread(target=tts_worker)
    playback_thread = threading.Thread(target=playback_worker)

    tts_thread.start()
    playback_thread.start()

    tts_thread.join()
    playback_thread.join()