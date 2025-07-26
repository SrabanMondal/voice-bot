import threading
import time
from stt.whisper_fast import transcribe_with_pause
#from model.model import generate_text
from model import generate_with_groq, generate_with_ollama
from tts import speak_text_multi, speak_text
from wakeup.wake import wake_word
import queue
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path
import os
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
def wake_thread(stop_event, sentence_queue):
    wake_word(stop_event, sentence_queue)
    
def llm_thread(text_queue,sentence_queue,stop_event):
    while True:
        try:
            text = text_queue.get(timeout=1)
            if text:
                print("LLm text - ",text)
                generate_with_groq(text, sentence_queue,stop_event,os.getenv("GROQ"))
        except queue.Empty:
            continue

def stt_thread(text_queue, stop_event):
    """
    Thread for continuous STT and LLM processing.
    Updates text_container with response, sets stop_event on 'stop'.
    """
    while True:
        #stop_event.clear()
        # Listen with pause detection
        if stop_event.is_set():
            input_text = transcribe_with_pause(text_queue)
            if not input_text:
                continue
            print(f"Transcribed: {input_text}")
            stop_event.clear()
            print("Whisper to sleep")
            if input_text.lower().strip() == "halt":
                print("Stop cmd: ",input_text)
                stop_event.set()
                continue


def tts_thread(sentence_queue, stop_event):
    """
    Thread for TTS, checks text_container, streams text, stops on stop_event.
    """
    while True:
        # Check for text or stop
        if not stop_event.is_set() and not sentence_queue.empty():
            print("🗣️ Speaking...")
            speak_text(sentence_queue, stop_event)
        else:
            time.sleep(0.3)

def main():
    
    text_queue = queue.Queue()
    stop_event = threading.Event()
    sentence_queue = queue.Queue()
    #stop_event.set()
    print("Thread starting")
    wake = threading.Thread(target=wake_thread, args=(stop_event,sentence_queue))
    stt = threading.Thread(target=stt_thread, args=(text_queue, stop_event))
    llm = threading.Thread(target=llm_thread, args=(text_queue,sentence_queue, stop_event))
    tts = threading.Thread(target=tts_thread, args=(sentence_queue, stop_event))
    wake.daemon = True
    stt.daemon = True
    tts.daemon = True
    llm.daemon = True
    wake.start()
    stt.start()
    tts.start()
    llm.start()
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_event.set()
        time.sleep(1)
if __name__ == "__main__":
    main()