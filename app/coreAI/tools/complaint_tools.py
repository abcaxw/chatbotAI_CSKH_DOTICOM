from langchain_core.tools import tool

import dlog
from coreAI import embedding_service

from database.dao.milvus.faq_dao import FaqDAO


@tool('retriever_complaint_tool')
def retriever_complaint_tool(complaint_information):
    """
    :param complaint_information: Nội dung phàn nàn khách hàng về các l
    :return:
    """
    vector = embedding_service.create_embedding(complaint_information)
    faq_dao = FaqDAO()
    faqs = faq_dao.search_by_vector(vector, limit=3)

    context = ""
    for index, faq in enumerate(faqs):
        context += f"{index + 1}. {faq[0]['answer']}\n"
    dlog.dlog_i(f"""retriever_complaint_tool: {context}""")
    return context
