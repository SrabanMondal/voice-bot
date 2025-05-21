from TTS.api import TTS
import pyaudio
import wave
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
print(tts.speakers)
tts.tts_to_file(
    text="Sun, mainu pata eh sab kuch hazam karna aukha hai, par tainu samajhna paina ke main eh faisla kyon kita. Jadon mauke darwaja khatkaunde ne, oh hamesha wait ni karde.",
    file_path="output.wav",
    speaker='Suad Qasim', 
    language="en"
)
p = pyaudio.PyAudio()
wf = wave.open('output.wav', 'rb')
stream = p.open(
                    format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
chunk = 1024
data = wf.readframes(chunk)
while data:
                    stream.write(data)
                    data = wf.readframes(chunk)

stream.stop_stream()
stream.close()
wf.close()
p.terminate()