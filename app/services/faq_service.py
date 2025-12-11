from coreAI import embedding_service
from database.dao.milvus.faq_dao import FaqDAO


def get_faqs_by_pagination(page_number, page_size, sort_type, title: str = None, question: str = None):
    faq_dao = FaqDAO()
    vector = None
    if question:
        vector = embedding_service.create_embedding(question)
    faqs, total_pages = faq_dao.get_faqs_by_pagination(page_number, page_size, sort_type, title, vector)

    return faqs, total_pages


def faqs_to_response(faqs, page_number, page_size, total_pages):
    faqs_data = [
        {
            "id": str(faq['id']),
            "title": faq["title"],
            "question": faq["question"],
            "answer": faq["answer"],
            "source": faq["source"],
            "created_at": faq["created_at"],
            "updated_at": faq["updated_at"]
        }
        for faq in faqs
    ]
    data = {
        "pageNumber": page_number,
        "pageSize": page_size,
        "totalPages": total_pages,
        "faqData": faqs_data
    }
    return data


def insert_faqs(faqs):
    faq_dao = FaqDAO()
    faqs_data = []
    create_time = faq_dao.create_time()
    for faq in faqs:
        data = faq.to_dict()
        embeddings = embedding_service.create_embedding(faq.question)
        data["vector"] = embeddings

        data["created_at"] = create_time
        data["updated_at"] = create_time
        faqs_data.append(data)
    faq_dao.insert_faqs(faqs_data)


def delete_faq_by_id(faq_id):
    faq_dao = FaqDAO()
    delete_count = faq_dao.delete_faq_by_ids([int(faq_id)])
    return delete_count


def delete_faq_by_question(question):
    faq_dao = FaqDAO()
    pass


def update_faq_by_id(faq_id, faq):
    faq_dao = FaqDAO()
    faq_data = faq.to_dict()
    faq_data["id"] = int(faq_id)
    faq_data["vector"] = embedding_service.create_embedding(faq.question)
    faq_dao.update_faq([faq_data])


def update_faq_by_question(faq):
    faq_dao = FaqDAO()
    pass


def get_faq_by_id(faq_id):
    faq_dao = FaqDAO()
    faq = faq_dao.get_faq_by_ids([int(faq_id)])
    if not faq:
        return None

    return faq[0]
