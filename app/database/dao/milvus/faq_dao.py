import math

import dlog

from database.dao.milvus.base_dao import BaseDAO


class FaqDAO(BaseDAO):
    def __init__(self):
        self.COLLECTION_NAME = "faq"
        self.client = self.get_client()

    def get_all_faqs(self):
        query = {'_id': 0, 'url': 1, 'question': 1, 'answer': 1, 'source': 1}
        records = self.client.find({}, query)
        dlog.dlog_i("Get all FAQs from milvus successfully")
        return list(records)

    def search_by_vector(self, vector, params=None, limit: int = 5):
        if params is None:
            params = {}
        result = self.client.search(
            collection_name=self.COLLECTION_NAME,
            data=[vector],
            limit=limit,
            search_params={"metric_type": "COSINE", "params": params},
            output_fields=["question", "answer", "id"]
        )
        return list(result)

    def get_faq_by_ids(self, ids: list):
        res = self.client.get(
            collection_name=self.COLLECTION_NAME,
            ids=ids,
            output_fields=["question", "answer", "id", "title", "source"]
        )
        return res

    def update_faq(self, faqs: list):
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            data=faqs
        )

    def delete_faq_by_ids(self, ids: list):
        delete_count = self.client.delete(
            collection_name=self.COLLECTION_NAME,
            ids=ids
        )
        return delete_count

    def delete_faq_by_filter(self, delete_filter: str):
        pass

    def insert_faqs(self, faqs):
        res = self.client.insert(
            collection_name=self.COLLECTION_NAME,
            data=faqs
        )
        return res

    def get_faqs_by_pagination(self, page_number, page_size, sort_type=None, title=None, vector=None):
        offset = (page_number - 1) * page_size
        result = self.client.query(collection_name=self.COLLECTION_NAME, output_fields=["count(*)"])
        total_hits = result[0]["count(*)"]
        total_pages = math.ceil(total_hits / page_size)
        if not vector:
            query_results = self.client.query(
                collection_name=self.COLLECTION_NAME,
                offset=offset,
                limit=page_size,
                # output_fields=["id", "question", "answer"],
            )
            return query_results, total_pages

        # Search with vector
        SEARCH_PARAM = {
            "collection_name": self.COLLECTION_NAME,

            "data": [vector],
            "anns_field": "vector",  # Replace with your vector field name
            "param": {"metric_type": "L2", "params": {"nprobe": 16}},  # Adjust metric_type and params as needed
            "limit": page_size,  # Initial limit, will be overridden by page_size in pagination logic
            "expr": None,  # Optional filter expression
            "output_fields": ["id", "question", "answer"],
            "offset": offset
        }
        results = self.client.search(**SEARCH_PARAM)
        hits_on_page = []
        for hit in results[0]:
            hits_on_page.append(hit.entity.to_dict())

        return hits_on_page, total_hits

    def get_total_count(self):
        """
        Lấy tổng số vector trong collection.
        (Nếu có filter điều kiện thì có thể thay đổi query)
        """
        collection = self.client.load_collection(collection_name=self.COLLECTION_NAME)
        count = collection.num_entities

        return count
