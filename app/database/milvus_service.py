from pymilvus import MilvusClient

import dlog


class MilvusService:
    def __init__(self, uri_connection: str, token: str, database_name: str):
        self.uri_connection = uri_connection
        self.token = token
        self.database_name = database_name
        self.client = None
        self.connect()

    def connect(self):
        try:
            self.client = MilvusClient(uri=self.uri_connection, token=self.token, db_name=self.database_name)
            dlog.dlog_i("Connected to Milvus successfully")
        except Exception as exc:
            dlog.dlog_e("Connected to Milvus Unsuccessfully")
            dlog.dlog_e(exc)

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            dlog.dlog_i("Disconnected to Milvus successfully")

    def get_health(self):
        if self.client.server_info():
            return True
        return False
