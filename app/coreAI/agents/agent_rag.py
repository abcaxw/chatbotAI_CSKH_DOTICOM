from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from coreAI import llm, embedding_service
from database import minio_service
from database.dao.mysql.document_dao import DocumentDAO
from database.dao.milvus.chunk_dao import ChunkDAO
from dconfig import config_prompts
import dlog


class RAG:
    def __init__(self):
        prompt = ChatPromptTemplate.from_template(config_prompts.RAG_PROMPT_TEMPLATE)
        self.chain = prompt | llm | StrOutputParser()


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    dlog.dlog_i("---RETRIEVE---")
    question = state["human_message"]

    # Retrieval
    vector = embedding_service.create_embedding(question)
    chunk_dao = ChunkDAO()
    chunks = chunk_dao.search_by_vector(vector, limit=5)

    # documents = documents[0:3]
    document_ids = [d["entity"]["document_id"] for d in chunks[0]]
    document_dao = DocumentDAO()
    documents = document_dao.get_documents_by_ids(document_ids)

    state["documents"] = documents
    return state


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    dlog.dlog_i("---GENERATE---")

    question = state["human_message"]
    documents = state["documents"]
    history = state.get("history", [])

    # RAG generation
    rag = RAG()
    contents = []
    for d in documents:
        url = minio_service.get_url_file(f'uploads/{d["filename"]}')
        content = d["content"] + url
        contents.append(content)
    context = "\n\n".join(contents)
    generation = rag.chain.invoke({"context": context, "history": history})
    state["ai_message"] = generation
    return state
