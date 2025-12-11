from database.dao.milvus.base_dao import BaseDAO
# from common_utils.time_utils import get_current_time
import dlog


class ThreadDAO(BaseDAO):
    def __init__(self):
        self.COLLECTION_NAME = "thread"
        self.client = self.get_client()

    def insert_thread(self, data):
        try:
            result = self.client.insert(
                collection_name=self.COLLECTION_NAME,
                data=data
            )
            dlog.dlog_i("Insert thread to milvus successfully")
            thread_id = None
            if result["insert_count"] > 0:
                thread_id = result.get("ids")[0]
            return thread_id
        except Exception as e:
            dlog.dlog_e("Insert thread to milvus error")
            dlog.dlog_e(e)

    def get_thread(self, platform, customer_id):
        query = f"platform like \"{platform}\" and user_id like \"{customer_id}\""
        record = self.client.query(collection_name=self.COLLECTION_NAME, filter=query, output_fields=["id"])
        dlog.dlog_i("Get thread from milvus successfully")
        return list(record)
