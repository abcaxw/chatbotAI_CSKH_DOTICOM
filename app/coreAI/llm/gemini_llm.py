import google.generativeai as genai

import dlog
from dconfig import config_object

gemini_1_5_flash = None
try:
    genai.configure(api_key=config_object.GOOGLE_API_KEY)
    gemini_1_5_flash = genai.GenerativeModel(model_name=config_object.GEMINI_MODEL_NAME)

    dlog.dlog_i(f"---INIT---: {config_object.GEMINI_MODEL_NAME}  llm successful")
except Exception as e:
    dlog.dlog_e(f"---INIT---: {config_object.GEMINI_MODEL_NAME} llm Unsuccessful {e}")
