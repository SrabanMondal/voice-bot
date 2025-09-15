# Voice Bot
A multi-threaded voice bot application that integrates speech-to-text (STT), text-to-speech (TTS), wake word detection, and a language model for real-time conversational capabilities. This project leverages a producer-consumer approach with parallel processing using threads and queues for fast inference on CPU.

# 📁 Project Structure

```
voice-bot/
├── app/
│   └── main.py               # Entry point to run the voice bot
├── model/
│   └── model.py              # LLM response generation logic
├── stt/
│   └── whisper_fast.py       # Fast Whisper transcription
├── tts/
│   └── coqui_tts_multi.py    # Coqui TTS for multi-lingual speech synthesis
├── wakeup/
│   ├── wake.py               # Porcupine wake word detection logic
│   └── your_wake_word.ppn    # (Add your .ppn wake word file here)
├── .env                      # Your Porcupine API key
├── requirements.txt          # Python dependencies
└── README.md                 # Project guide
```

## ⚙️ Prerequisites
Before running the bot, make sure your system has the following installed:

## 🔊 Audio Dependencies
ffmpeg: Required for audio processing (used by Whisper)

portaudio: For PyAudio microphone input

## ⚙️ Build Tools (for llama-cpp-python)
cmake and C/C++ Build Tools:

On Ubuntu: sudo apt install build-essential cmake

On Windows: Install "Build Tools for Visual Studio" with C++ components

### Python version: 3.12 (ideally 3.12.3)

## 🔑 Setting Up Wake Word Detection
Sign up at Picovoice Console and:

Get your Access Key

Create and download a custom wake word (.ppn) file

Place your .ppn file inside the wakeup/ folder.

Open wakeup/wake.py and update the file name in the Porcupine config:
keyword_paths=["your_wake_word.ppn"]

## Create a .env file in the root with your key:

PORCUPINE=your-access-key-here

## 📦 Installation
Clone the repo and navigate to it:
```sh
git clone https://github.com/SrabanMondal/voice-bot.git
=======
git clone https://github.com/your-username/voice-bot.git
cd voice-bot
```
Install Python dependencies:
```sh
pip install -r requirements.txt
```

▶️ Running the Voice Bot
After setup, simply run:
```sh
python -m app.main
```
Make sure your microphone is enabled and you’re using Python 3.12 (exact version 3.12.3 is best for compatibility with llama-cpp-python).

## Technical Details
- **Multi-Threading**: Each component (STT, TTS, wake word detection, and LLM) runs in its own thread for concurrent execution, improving responsiveness.  

- **Producer-Consumer Approach**: The TTS module uses a producer-consumer pattern with parallel processing via threads to achieve fast text-to-speech conversion.
  
- **Token Streaming**: Queues are utilized to stream tokens from the language model to the TTS module, enabling efficient CPU-based inference.

- **Testing Status**: The project is functional but requires extensive testing to ensure stability and performance under various conditions.
