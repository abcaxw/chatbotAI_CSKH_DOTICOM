from database.dao.milvus.base_dao import BaseDAO
import dlog


class CustomerDAO(BaseDAO):
    def __init__(self):
        self.COLLECTION_NAME = "customer"
        self.client = self.get_client()

    def insert_customer(self, data):
        try:
            result = self.client.insert(
                collection_name=self.COLLECTION_NAME,
                data=data
            )
            dlog.dlog_i("Insert customer to milvus successfully")
            customer_id = None
            if result["insert_count"] > 0:
                customer_id = result.get("ids")[0]
            return customer_id
        except Exception as e:
            dlog.dlog_e("Insert customer to milvus error")
            dlog.dlog_e(e)

    def get_customer_by_platform(self, platform, platform_customer_id):
        query = f"platform like \"{platform}\" and platform_customer_id like \"{platform_customer_id}\""
        self.client.load_collection(collection_name=self.COLLECTION_NAME)
        record = self.client.query(collection_name=self.COLLECTION_NAME, filter=query, output_fields=["id"])
        dlog.dlog_i("Get customer from milvus successfully")
        return list(record)
