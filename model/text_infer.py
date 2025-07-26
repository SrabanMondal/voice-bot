import os
import threading
import itertools
import re
import string
import requests
import json
import time
from queue import Queue
from typing import Callable
from ollama import Client as OllamaClient

# Optional: Lock for shared buffer access
buffer_lock = threading.Lock()
token_buffer = []

# Utility: Check if a sentence is just punctuation
def is_only_punctuation(text):
    text = text.strip()
    return all(char in string.punctuation for char in text) and len(text) > 0

# Tokenizer for punctuation/word splitting
def tokenize(text):
    text = text.strip()
    pattern = r"\s+\w+|\w+|[^\w\s]"
    return re.findall(pattern, text)

# Token streaming handler -> queues sentence-wise responses
def stream_token_handler(token: str, sentence_queue: Queue, counter: iter):
    with buffer_lock:
        token_buffer.append(token)
        if token.endswith((".", "!", "?", ",")):
            sentence = ''.join(token_buffer).strip()
            if sentence and not is_only_punctuation(sentence):
                idx = next(counter)
                print(f"token {idx} : {sentence}")
                sentence_queue.put((idx, sentence))
                token_buffer.clear()

### 🔥 1. Local LLM: Using Ollama (e.g., llama3)
def generate_with_ollama(user_prompt: str, sentence_queue: Queue, stop_event: threading.Event):
    global token_buffer
    token_buffer = []
    counter = itertools.count()
    
    client = OllamaClient(host='http://localhost:11434')  # default ollama host
    stream = client.chat(
        model='llama3',  # Make sure llama3 is pulled in Ollama: `ollama pull llama3`
        messages=[{"role": "user", "content": user_prompt}],
        stream=True
    )

    try:
        for chunk in stream:
            if stop_event.is_set():
                break
            token = chunk.get("message", {}).get("content", "")
            if token:
                stream_token_handler(token, sentence_queue, counter)

        # Flush remaining tokens if any
        with buffer_lock:
            if token_buffer:
                sentence = ''.join(token_buffer).strip()
                if sentence:
                    idx = next(counter)
                    sentence_queue.put((idx, sentence))
                    token_buffer.clear()
        sentence_queue.put(None)

    except Exception as e:
        print(f"[OLLAMA] Error: {e}")
        sentence_queue.put(None)

### ☁️ 2. Cloud LLM: Using Groq API
def generate_with_groq(user_prompt: str, sentence_queue: Queue, stop_event: threading.Event, api_key: str):
    global token_buffer
    token_buffer = []
    counter = itertools.count()

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{"role": "user", "content": user_prompt}],
        "stream": True
    }

    try:
        with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
            for line in response.iter_lines():
                if stop_event.is_set():
                    break
                if line:
                    decoded = line.decode('utf-8').replace("data: ", "")
                    if decoded.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(decoded)
                        token = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if token:
                            stream_token_handler(token, sentence_queue, counter)
                    except json.JSONDecodeError:
                        continue

        with buffer_lock:
            if token_buffer:
                sentence = ''.join(token_buffer).strip()
                if sentence:
                    idx = next(counter)
                    sentence_queue.put((idx, sentence))
                    token_buffer.clear()
        sentence_queue.put(None)

    except Exception as e:
        print(f"[GROQ] Error: {e}")
        sentence_queue.put(None)

