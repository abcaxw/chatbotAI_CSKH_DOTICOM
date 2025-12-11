import dlog
from database.dao.milvus.base_dao import BaseDAO


class DocumentDAO(BaseDAO):

    def __init__(self):
        self.COLLECTION_NAME = "document"
        self.client = self.get_client()

    def get_documents_by_ids(self, ids):
        self.client.load_collection(collection_name=self.COLLECTION_NAME)
        record = self.client.query(collection_name=self.COLLECTION_NAME, ids=ids, output_fields=["content"])
        dlog.dlog_i("Get document from milvus successfully")
        return list(record)

    def insert_documents(self, documents):
        result = self.client.insert(
            collection_name=self.COLLECTION_NAME,
            data=documents
        )
        document_id = None
        if result["insert_count"] > 0:
            document_id = result.get("ids")[0]
        return document_id
