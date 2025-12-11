from langchain_openai import ChatOpenAI

import dlog
from coreAI.cake_detector import Yolo11CakeDetector
from coreAI.image_embedding import ImageEmbedder
from coreAI.text_embedding import EmbeddingService
from dconfig import config_object, config_models

embedding_service = None

try:

    embedding_service = EmbeddingService(config_object.OPENAI_API_KEY)
    dlog.dlog_i("---INIT---:  Load open embedding successful")
except Exception as e:
    dlog.dlog_e(f"---INIT---:  Load open embedding Unsuccessful {e}")

llm = None
try:
    llm = ChatOpenAI(model=config_object.LLM_MODEL_4O, api_key=config_object.OPENAI_API_KEY,
                     seed=42, top_p=0.2, temperature=0)
    dlog.dlog_i("Successfully initialized GPT LLM")

except Exception as e:
    dlog.dlog_i("Error initializing GPT LLM")
    dlog.dlog_e(e)

order_llm = None
try:
    order_llm = ChatOpenAI(model=config_object.LLM_MODEL, api_key=config_object.OPENAI_API_KEY,
                           seed=42, top_p=0.2, temperature=0)
    dlog.dlog_i("Successfully initialized order_llm")

except Exception as e:
    dlog.dlog_i("Error initializing order_llm")
    dlog.dlog_e(e)

embedding_image_model = None
try:

    embedding_image_model = ImageEmbedder(model_path=config_models.MODEL_EMBEDDING_IMAGE)
    dlog.dlog_i("Successfully initialized embedding image model")

except Exception as e:
    dlog.dlog_i("Error initializing embedding image model")
    dlog.dlog_e(e)

cake_detector = None
try:

    cake_detector = Yolo11CakeDetector(model_weights=config_models.MODEL_CAKE_DETECT)
    dlog.dlog_i("Successfully initialized cake detector")

except Exception as e:
    dlog.dlog_i("Error initializing cake detector")
    dlog.dlog_e(e)