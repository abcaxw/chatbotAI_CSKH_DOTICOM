import uuid
from dataclasses import dataclass
from typing import List
from datetime import datetime

from database import milvus_service


@dataclass
class BaseDAO:
    COLLECTION_NAME = ""

    @staticmethod
    def get_client():
        client = milvus_service.client
        return client

    def create_uuids(self, number: int) -> List:
        uuids = [self.create_uuid() for _ in range(number)]
        return uuids

    def create_uuid(self):
        return str(uuid.uuid4())

    def create_time(self):
        now = datetime.now()
        # Convert datetime to string in the desired format
        formatted_time = now.strftime("%d-%m-%Y %H:%M:%S")
        return str(formatted_time)

    def create_timestamp(self):
        now = datetime.now().timestamp()
        return now