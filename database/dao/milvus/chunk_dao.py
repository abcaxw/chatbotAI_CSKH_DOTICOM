from database.dao.milvus.base_dao import BaseDAO


class ChunkDAO(BaseDAO):
    def __init__(self):
        self.COLLECTION_NAME = "chunk"
        self.client = self.get_client()

    def search_by_vector(self, vector, params=None, limit: int = 5):
        if params is None:
            params = {}
        result = self.client.search(
            collection_name=self.COLLECTION_NAME,
            data=[vector],
            limit=limit,
            group_by_field="document_id",
            group_size=2,
            group_strict_size=True,
            search_params={"metric_type": "COSINE", "params": params},
            output_fields=["document_id"]
        )
        return list(result)

    def get_chunks_by_ids(self, ids: list):
        res = self.client.query(
            collection_name=self.COLLECTION_NAME,
            ids=ids,
        )

        return res

    def update_chunks(self, documents: list):
        pass

    def delete_chunks_by_ids(self, ids: list):
        pass

    def delete_chunks_by_filter(self, delete_filter: str):
        res = self.client.delete(
            collection_name=self.COLLECTION_NAME,
            filter=delete_filter
        )
        return res

    def insert_chunks(self, chunks):
        res = self.client.insert(
            collection_name=self.COLLECTION_NAME,
            data=chunks
        )
        return res
