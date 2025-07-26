import pvporcupine
import pyaudio
import struct
import os
import queue
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Access environment variables
PORCUPINE = os.getenv("PORCUPINE")
def clear_queue(q):
    with q.mutex:
        q.queue.clear()
        q.all_tasks_done.notify_all()
        q.unfinished_tasks = 0

WAKEUP_DIR = os.path.dirname(os.path.abspath(__file__))
def wake_word(stop_event, sentence_queue):
    print("[ACCESS KEY]: ",PORCUPINE)
    porcupine = pvporcupine.create(
        access_key=PORCUPINE,
        keyword_paths=[os.path.join(WAKEUP_DIR, "devil.ppn")]
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:
                print("Model is awake")
                stop_event.set()
                clear_queue(sentence_queue)
    except KeyboardInterrupt:
        print("Exiting Wake Up")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
