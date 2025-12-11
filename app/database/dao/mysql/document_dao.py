from typing import List, Optional
from mysql.connector import Error

import dlog
from database.dao.mysql.base_dao import BaseDAO
from object_models.db_obj import DocumentPaginationData, Document


class DocumentDAO(BaseDAO):
    def __init__(self):
        self.connection = self.get_client()
        self.COLLECTION_NAME = "documents"

    def get_all_documents(self, page: int, page_size: int) -> List[dict]:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM {self.COLLECTION_NAME} LIMIT %s OFFSET %s"
        try:
            # self.connection = self.get_client()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (page_size, offset))
                return cursor.fetchall()
        except Error as exc:
            dlog.dlog_e(exc)
            return []

    def get_document_by_id(self, doc_id: int) -> Optional[dict]:
        query = f"""SELECT d.*, u.username AS username ,c.name AS category
                 FROM {self.COLLECTION_NAME} d
                 JOIN user u ON d.user_id = u.id
                 JOIN categories c ON d.category_id = c.id
                 WHERE d.id = %s"""
        try:
            # self.connection = self.get_client()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (doc_id,))
                doc = cursor.fetchone()
                result = self.convert_formattime_one(doc)
                return result
        except Error as exc:
            dlog.dlog_e(exc)
            return None

    def get_documents_by_pagination(self, document_pagination_data: DocumentPaginationData) -> tuple[list, int]:
        offset = (document_pagination_data.page_number - 1) * document_pagination_data.page_size
        query = f"""
        SELECT d.*, c.name AS category,u.username AS username, COUNT(*) OVER() AS total_document
        FROM {self.COLLECTION_NAME} d
        JOIN user u ON d.user_id = u.id
        JOIN categories c ON d.category_id = c.id
        WHERE (%s IS NULL OR u.username LIKE %s)
        AND (%s IS NULL OR c.id = %s)
        AND (%s IS NULL OR d.title = %s)
        AND (%s IS NULL OR d.url = %s)
        LIMIT %s OFFSET %s;"""
        try:
            # self.connection = self.get_client()
            with self.connection.cursor(dictionary=True) as cursor:
                username = f"%{document_pagination_data.creator}%"
                cursor.execute(query, (
                    document_pagination_data.creator, username,
                    document_pagination_data.category_id, document_pagination_data.category_id,
                    document_pagination_data.title, document_pagination_data.title,
                    document_pagination_data.url, document_pagination_data.url,
                    document_pagination_data.page_size, offset))
                result = cursor.fetchall()
                result = self.convert_formattime(result)
                total_document = result[0]['total_document'] if result else 0
                return result, total_document
        except Error as exc:
            dlog.dlog_e(exc)
            return [], 0

    def update_document_by_id(self, doc_id: int, document: Document) -> bool:
        query = f"""
        UPDATE {self.COLLECTION_NAME}
        SET content = %s, title = %s, category_id = %s, updated_at = NOW()
        WHERE id = %s
        """
        try:
            # self.connection = self.get_client()
            with self.connection.cursor() as cursor:
                cursor.execute(query, (document.content, document.title, document.category_id, doc_id))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error as exc:
            dlog.dlog_e(exc)
            return False

    def delete_document_by_id(self, doc_id: int) -> bool:
        query = f"DELETE FROM {self.COLLECTION_NAME} WHERE id = %s"
        try:
            self.connection = self.get_client()
            with self.connection.cursor() as cursor:
                cursor.execute(query, (doc_id,))
                self.connection.commit()
                return cursor.rowcount
        except Error as exc:
            dlog.dlog_e(exc)
            return False

    def insert_document(self, document: Document) -> bool:
        query = f"""
        INSERT INTO {self.COLLECTION_NAME} (content, filename, title, url, category_id, user_id, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        try:
            # self.connection = self.get_client()
            with self.connection.cursor() as cursor:
                cursor.execute(query, (document.content, document.filename,
                                       document.title, document.url, document.category_id, document.user_id))
                self.connection.commit()
                return cursor.lastrowid
        except Error as exc:
            dlog.dlog_e(exc)
            return False

    def get_documents_by_ids(self, doc_ids: List[int]) -> List[dict]:
        if not doc_ids:
            return []
        format_strings = ','.join(['%s'] * len(doc_ids))
        query = f"SELECT * FROM {self.COLLECTION_NAME} WHERE id IN ({format_strings})"
        try:
            # self.connection = self.get_client()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(doc_ids))
                return cursor.fetchall()
        except Error as exc:
            dlog.dlog_e(exc)
            return []

    def update_content_by_document_id(self, doc_id: int, content: str) -> bool:
        query = f"UPDATE {self.COLLECTION_NAME} SET content = %s WHERE id = %s"
        try:
            self.connection = self.get_client()
            with self.connection.cursor() as cursor:
                cursor.execute(query, (content, doc_id))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error as exc:
            dlog.dlog_e(exc)
            return False
