# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
# from pathlib import Path

# # Load .env file from root directory
# env_path = Path(__file__).resolve().parent.parent / '.env'
# load_dotenv(dotenv_path=env_path)

# # Access environment variables
# SECRET_KEY = os.getenv('GEMINI_API')
# genai.configure(api_key=SECRET_KEY)

# def generate_text(text, target_lang="Hindi"):
#     model = genai.GenerativeModel("gemini-2.0-flash")
    
#     #prompt = f"Answer the following query concisely in 20 words in clean text: {text}"
#     prompt = f"""You are a accurate translator. Translate the query into punjabi language but written in english language, i.e, punjabinglish

#             Query: {text}
            
#             #Guidelines
#             1. Give clean text
#             2. Give only exact translated text"""
#     try:
#         # Generate response
#         response = model.generate_content(prompt)
#         return response.text.strip()
#     except Exception as e:
#         print(f"Error generating response: {e}")
#         return "Sorry, I couldn't process that request."
# import requests
# def translate_mymemory(text, source_lang="en", target_lang="pa"):
#     url = "https://api.mymemory.translated.net/get"
#     params = {"q": text, "langpair": f"{source_lang}|{target_lang}"}
#     response = requests.get(url, params=params)
#     return response.json()["responseData"]["translatedText"]
# import requests
# import time
# text = '''Look, I know it’s a lot to process right now, but you need to understand why I made the decision I did. When opportunities come knocking, they don’t always wait around. '''
# s = time.time()
# print(generate_text(text))
# #print(translate_mymemory(text))
# #print(translate_m2m100(text))
# e = time.time()
# print('latency: ',e-s)