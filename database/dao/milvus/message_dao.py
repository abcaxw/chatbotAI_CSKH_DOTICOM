from database.dao.milvus.base_dao import BaseDAO


class MessageDAO(BaseDAO):
    def __init__(self):
        self.COLLECTION_NAME = "message"
        self.client = self.get_client()

    def get_message_by_(self, ids: list):
        res = self.client.query(
            collection_name=self.COLLECTION_NAME,
            ids=ids,
        )

        return res

    def get_messages_by_filter(self, filter, output_fields, search_params, limit: int = 5):
        record = self.client.query(
            collection_name=self.COLLECTION_NAME,
            filter=filter,
            output_fields=output_fields,
            limit=limit,
            search_params=search_params
        )

        return list(record)

    def count_message(self, filter):
        record = self.client.query(
            collection_name=self.COLLECTION_NAME,
            filter=filter,
            output_fields=["count(*)"],

        )

        return record

    def update_message(self, message: list):
        pass

    def delete_message_by_id(self, id: str):
        pass

    def delete_message_by_filter(self, delete_filter: str):
        pass

    def insert_message(self, message):
        res = self.client.insert(
            collection_name=self.COLLECTION_NAME,
            data=message
        )
        return res

    def update_platform_message_id(self, message_id, platform_message_id):
        results = self.client.query(
            collection_name=self.COLLECTION_NAME,
            ids=[message_id],
            output_fields=["*"]
        )
        if len(results) == 0:
            return message_id
        message_info = results[-1]
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            ids=[message_id]
        )

        message_info["platform_message_ids"].append(str(platform_message_id))
        message_info.pop('id')
        update_result = self.client.insert(
            collection_name=self.COLLECTION_NAME,
            data=message_info
        )
        return update_result["ids"][-1]
