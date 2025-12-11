from typing import List, Optional
from mysql.connector import Error

import dlog
from database.dao.mysql.base_dao import BaseDAO
from object_models.db_obj import PaginationData, Category


class CategoryDAO(BaseDAO):
    def __init__(self):
        self.connection = self.get_client()
        self.COLLECTION_NAME = "categories"

    def get_all_categories(self) -> List[dict]:
        query = f"SELECT * FROM {self.COLLECTION_NAME}"
        try:
            # self.connection = self.get_client()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                categories = cursor.fetchall()
                categories = self.convert_formattime(categories)
                return categories
        except Error as exc:
            dlog.dlog_e(exc)
            return []

    def get_category_by_id(self, category_id: int) -> Optional[dict]:
        query = f"""SELECT c.*
                 FROM {self.COLLECTION_NAME} c
                 WHERE c.id = %s"""
        try:
            # self.connection = self.get_client()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (category_id,))
                doc = cursor.fetchone()
                doc = self.convert_formattime_one(doc)
                return doc
        except Error as exc:
            dlog.dlog_e(exc)
            return None

    def get_categories_by_pagination(self, pagination_data: PaginationData) -> tuple[list, int]:
        offset = (pagination_data.page_number - 1) * pagination_data.page_size
        query = f"""
        SELECT c.*, COUNT(*) OVER() AS total_categories
        FROM {self.COLLECTION_NAME} c
        LIMIT %s OFFSET %s;"""
        try:
            # self.connection = self.get_client()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (pagination_data.page_size, offset))

                result = cursor.fetchall()
                result = self.convert_formattime(result)
                total_categories = result[0]['total_categories'] if result else 0
                return result, total_categories
        except Error as exc:
            dlog.dlog_e(exc)
            return [], 0

    def delete_category_by_id(self, category_id: int) -> bool:
        query = f"DELETE FROM {self.COLLECTION_NAME} WHERE id = %s"
        try:
            # self.connection = self.get_client()
            with self.connection.cursor() as cursor:
                cursor.execute(query, (category_id,))
                self.connection.commit()
                return cursor.rowcount
        except Error as exc:
            dlog.dlog_e(exc)
            return False

    def insert_category(self, category: Category) -> bool:
        query = f"""
        INSERT INTO {self.COLLECTION_NAME} (name, created_at, updated_at)
        VALUES (%s, NOW(), NOW())
        """
        try:
            # self.connection = self.get_client()
            with self.connection.cursor() as cursor:
                cursor.execute(query, (category.name,))
                self.connection.commit()
                return cursor.lastrowid
        except Error as exc:
            dlog.dlog_e(exc)
            return False

    def update_category_by_id(self, category_id: int, name: str) -> bool:
        query = f"UPDATE {self.COLLECTION_NAME} SET name = %s WHERE id = %s"
        try:
            self.connection = self.get_client()
            with self.connection.cursor() as cursor:
                cursor.execute(query, (name, category_id))
                self.connection.commit()
                return cursor.rowcount > 0
        except Error as exc:
            dlog.dlog_e(exc)
            return False