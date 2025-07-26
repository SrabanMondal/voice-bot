# #import google.generativeai as genai
# #from dotenv import load_dotenv
# import os
# import threading
# import itertools
# import time
# import re
# import string
# from llama_cpp import Llama
# from huggingface_hub import hf_hub_download
# model_path = hf_hub_download(
#     repo_id="srabanmondal/mistral_cpu",  # replace with your actual repo
#     filename="model.gguf",
#     repo_type="model"
# )

# print(f"Model path: {model_path}")
# #MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
# def is_only_punctuation(text):
#     text=text.strip()
#     return all(char in string.punctuation for char in text) and len(text) > 0


# def tokenize(text):
#     text = text.strip()
#     pattern = r"\s+\w+|\w+|[^\w\s]"
#     raw_tokens = re.findall(pattern, text)
#     tokens = [token for token in raw_tokens]
#     return tokens

# # Load .env file from root directory
# #env_path = Path(__file__).resolve().parent.parent / '.env'
# #load_dotenv(dotenv_path=env_path)

# # Access environment variables
# SECRET_KEY = os.getenv('GEMINI_API')
# #genai.configure(api_key=SECRET_KEY)
# #token_buffer = []
# buffer_lock = threading.Lock()

# def stream_token_handler(token,sentence_queue, counter): 
#     with buffer_lock:
#         token_buffer.append(token)
#         if token.endswith((".", "!", "?",',')):
#             sentence = ''.join(token_buffer).strip()
#             if sentence and not is_only_punctuation(sentence):
#                 idx = next(counter)
#                 print('token ',idx,' : ',sentence)
#                 sentence_queue.put((idx, sentence))
#                 token_buffer.clear()
# def generate_text(text,sentence_queue, stop_event):
#     global token_buffer

# # Path to your GGUF 4-bit model file
#     #model_path = os.path.join(MODEL_DIR, "unsloth.Q4_K_M.gguf")

# # Load the model (adjust n_ctx as needed for your use case)
#     llm = Llama(
#         model_path=model_path,
#         n_ctx=1024,         # context length
#         n_threads=8,        # number of CPU threads to use
#         use_mlock=True,     # optional: pin model in RAM for faster access
#     )
#     prompt = """[INST] {} [/INST] {}"""
#     text = prompt.format(text,"")
#     token_buffer = []
#     counter = itertools.count()
#     try:
#         # Generate response
#         #text = 'Photosynthesis is the process where plants convert sunlight into chemical energy, specifically glucose, using carbon dioxide and water, and releasing oxygen as a byproduct. This process allows plants to make their own food, forming the base of the food chain for most ecosystems.'
#         #response = tokenize(text)
#         for chunk in llm(text, max_tokens=512, stream=True):
#             #print(chunk["choices"][0]["text"], end="", flush=True)
#             stream_token_handler(chunk["choices"][0]["text"],sentence_queue, counter)
#             if stop_event.is_set():
#                 return
#         # for token in response:
#         #     time.sleep(0.5)
            
#         with buffer_lock:
#             if token_buffer:
#                 sentence = ''.join(token_buffer).strip()
#                 if sentence:
#                     idx = next(counter)
#                     sentence_queue.put((idx, sentence))
#                     token_buffer.clear()
#         for _ in range(2):
#             sentence_queue.put(None)
#     except Exception as e:
#         print(f"Error generating response: {e}")