from database.dao.milvus.base_dao import BaseDAO


class BillDAO(BaseDAO):
    def __init__(self):
        self.COLLECTION_NAME = "bills"
        self.client = self.get_client()

    def get_bills_by_ids(self, ids: list):
        res = self.client.query(
            collection_name=self.COLLECTION_NAME,
            ids=ids,
        )

        return res

    def get_bills_by_customer(self, filter, output_fields, limit: int = 5):
        record = self.client.query(
            collection_name=self.COLLECTION_NAME,
            filter=filter,
            output_fields=output_fields,
            limit=limit,
            order_by_field="created_at",
            order="desc",
        )

        return list(record)

    def count_bills(self, filter):
        record = self.client.query(
            collection_name=self.COLLECTION_NAME,
            filter=filter,
            output_fields=["count(*)"]
        )

        return record

    def update_bill(self, bill_id: str, bill_data):
        pass

    def insert_bill(self, bill):
        res = self.client.insert(
            collection_name=self.COLLECTION_NAME,
            data=bill
        )
        return res

