import os
import shutil
import time

import requests

import dconfig

from object_models.exceptions import InputFileException
from urllib.parse import urlparse

DATA_DIR = dconfig.config_object.DATA_DIR
TEMP_DIR = os.path.join(DATA_DIR, 'temp')


def save_fastapi_request_file(url_file):
    filename = url_file.filename
    extension = filename[filename.rfind('.'):].lower()

    timestamp = time.time_ns()
    file = os.path.join(TEMP_DIR, f'{timestamp}{extension}')
    if os.path.isfile(file):
        timestamp += 1
        file = os.path.join(TEMP_DIR, f'{timestamp}{extension}')
    with open(file, "wb") as buffer:
        shutil.copyfileobj(url_file.file, buffer)

    if isinstance(file, dict):
        raise InputFileException()
    if file is None:
        raise InputFileException()
    return file


def delete_file(filepath):
    if filepath is not None and (os.path.isfile(filepath) or os.path.islink(filepath)):
        os.unlink(filepath)

def download_image(url, save_path=None):
    if save_path is None:
        path = urlparse(url).path
        extension  = os.path.splitext(path)[1]
        timestamp = time.time_ns()
        save_path = os.path.join(TEMP_DIR, f'{timestamp}{extension}')
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    return save_path

def load_prompt(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    return system_prompt