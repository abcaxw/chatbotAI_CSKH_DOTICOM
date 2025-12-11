import math
import os

from pyvi.ViTokenizer import tokenize

import dlog
from common_utils.string_utils import text2chunks
from coreAI import embedding_service

from database import minio_service
from database.dao.milvus.chunk_dao import ChunkDAO
from database.dao.mysql.document_dao import DocumentDAO

from dconfig import config_object
from services.pdf_service import pdf2text


def insert_document(path_file, document):
    dlog.dlog_i(f"---INSERT document {document.filename}")
    document_dao = DocumentDAO()
    # if path_file:

    filename_origin = None
    if not document.content and path_file is not None:
        filename_origin = os.path.basename(path_file)
        document.content, file_name = pdf2text(path_file)
        path_file = path_file.replace(filename_origin, file_name)
        filename_origin = file_name

        minio_service.upload_file(path_file, f'uploads/{filename_origin}', document.doc_type)
        url = f"{config_object.DOMAIN_MINIO}/chatbot/uploads/{filename_origin}"
        document.filename = filename_origin
        document.url = url
    document_id = document_dao.insert_document(document)
    if not document.content:
        insert_chunks(document_id, document.content)
    return document_id, document.content


def insert_chunks(document_id, text):
    chunk_dao = ChunkDAO()
    created_at = chunk_dao.create_time()
    splits = text2chunks(text, config_object.CHUNK_SIZE, config_object.CHUNK_OVERLAP)
    chunks = []
    for index, split in enumerate(splits):
        vector = embedding_service.create_embedding(split.page_content)

        chunk = {
            "document_id": document_id,
            "chunk_index": f"{index + 1}",
            "content": split.page_content,
            "vector": vector,
            "created_at": created_at,
            "updated_at": created_at
        }
        chunks.append(chunk)
    chunk_dao.insert_chunks(chunks)
    dlog.dlog_i(f"---FINISH INSERT CHUNK by document_id {document_id}")


def get_documents_by_pagination(document_pagination_data):
    document_dao = DocumentDAO()
    documents, total_document = document_dao.get_documents_by_pagination(document_pagination_data)
    total_pages = math.ceil(total_document / document_pagination_data.page_size)
    dlog.dlog_i(f"---FINISH GET documents  by pagination")
    for document in documents:
        url = minio_service.get_url_file(f'uploads/{document["filename"]}')
        document["url"] = url
    return documents, total_pages


def get_document_by_id(document_id):
    document_dao = DocumentDAO()
    document = document_dao.get_document_by_id(document_id)
    return document


def update_document_by_id(document_id, document):
    document_dao = DocumentDAO()
    document_dao.update_document_by_id(document_id, document)
    delete_chunks_by_document_id(document_id)
    dlog.dlog_i(f"---FINISH UPDATE document_id {document_id}")


def delete_chunks_by_document_id(document_id):
    chunk_dao = ChunkDAO()
    filter = f"document_id == {document_id}"
    chunk_dao.delete_chunks_by_filter(filter)
    dlog.dlog_i(f"---FINISH DELETE chunks by document_id {document_id}")


def delete_document_by_id(document_id):
    document_dao = DocumentDAO()
    delete_count = document_dao.delete_document_by_id(document_id)
    delete_chunks_by_document_id(document_id)
    dlog.dlog_i(f"---FINISH DELETE document_id {document_id}")
    return delete_count


def update_content_by_document_id(document_id, content):
    document_dao = DocumentDAO()
    document_dao.update_content_by_document_id(document_id, content)
