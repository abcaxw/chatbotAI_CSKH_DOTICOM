import json
import os

import yaml
from dotenv import load_dotenv
from starlette.templating import Jinja2Templates

load_dotenv()


# declaring a class
class ConfigObj:
    # constructor
    def __init__(self, dict1):
        self.__dict__.update(dict1)


def dict2obj(dict1):
    # using json.loads method and passing json.dumps
    # method and custom object hook as arguments
    return json.loads(json.dumps(dict1), object_hook=ConfigObj)


def yaml2obj(yaml_path):
    with open(yaml_path) as f:
        data_load = yaml.safe_load(f)

    config_obj = dict2obj(data_load)

    return config_obj


config_object = yaml2obj(os.getenv("CONFIG_PATH"))
config_object.LOG_DIR = os.getenv("LOG_DIR")
config_object.DATA_DIR = os.getenv("DATA_DIR")

config_object.SECRET_AUTH_KEY = os.getenv("SECRET_AUTH_KEY")

config_object.PAGE_FACEBOOK_ACCESS_TOKEN = os.getenv("PAGE_FACEBOOK_ACCESS_TOKEN")
config_object.PAGE_FACEBOOK_VERIFY_TOKEN = os.getenv("PAGE_FACEBOOK_VERIFY_TOKEN")
config_object.PAGE_FACEBOOK_DOMAIN = os.getenv("PAGE_FACEBOOK_DOMAIN")
config_object.TOKEN_CONNECTION_MILVUS = os.getenv("TOKEN_CONNECTION_MILVUS")

config_object.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
config_object.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

config_object.ORS_API_KEY = os.getenv("ORS_API_KEY")



config_prompts = yaml2obj(os.getenv("PROMPTS_PATH"))
config_models = yaml2obj(os.getenv("MODELS_PATH"))
config_messages = yaml2obj(os.getenv("MESSAGES_PATH"))
config_agents = yaml2obj(os.getenv("AGENTS_PATH"))

config_prompts_path = yaml2obj(os.getenv("PROMPTS_PATH_LIST"))

# Cấu hình Jinja2Templates với các hàm bổ sung
templates = Jinja2Templates(directory=config_object.TEMPLATE_DIR)
templates.env.globals.update({
    "max": max,
    "min": min,
})
# Đặt templates vào config để các route có thể truy cập
config_object.TEMPLATES = templates
