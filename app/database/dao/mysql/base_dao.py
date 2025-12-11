from dataclasses import dataclass
from datetime import datetime

from database import mysql_service


@dataclass
class BaseDAO:
    COLLECTION_NAME = ""

    @staticmethod
    def get_client():
        if not mysql_service.connection.is_connected():
            mysql_service.connect()
        client = mysql_service.connection
        return client

    def create_timestamp(self):
        now = datetime.now().timestamp()
        return now

    def convert_formattime(self, result: list):
        for doc in result:
            doc = self.convert_formattime_one(doc)
        return result

    def convert_formattime_one(self, result: dict):
        for field in ['created_at', 'updated_at']:
            if field in result and isinstance(result[field], datetime):
                result[field] = result[field].strftime('%Y-%m-%d %H:%M:%S')
        return result
