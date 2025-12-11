from typing import List, Optional
from mysql.connector import Error

import dlog
from database.dao.mysql.base_dao import BaseDAO


class UserDAO(BaseDAO):
    def __init__(self):
        self.connection = self.get_client()

    def get_all_users(self, page: int, page_size: int) -> List[dict]:
        offset = (page - 1) * page_size
        query = "SELECT * FROM user LIMIT %s OFFSET %s"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (page_size, offset))
            return cursor.fetchall()
        except Error as exc:
            dlog.dlog_e(exc)
            return []

    def get_user_by_username_password(self, username: str, password: str) -> Optional[dict]:
        query = "SELECT * FROM user WHERE username = %s AND password = %s"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (username, password))
            return cursor.fetchone()
        except Error as exc:
            dlog.dlog_e(exc)
            return None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        query = "SELECT * FROM user WHERE username = %s"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (username,))
            return cursor.fetchone()
        except Error as exc:
            dlog.dlog_e(exc)
            return None

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        query = "SELECT * FROM document WHERE id = %s"
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        except Error as exc:
            dlog.dlog_e(exc)
            return None

    def delete_user_by_id(self, doc_id: int) -> bool:
        query = "DELETE FROM document WHERE id = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (doc_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as exc:
            dlog.dlog_e(exc)
            return False

    def insert_user(self, role: str, username: str, phone: str, password: str) -> bool:
        query = """
        INSERT INTO user (role, username, phone, password, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (role, username, phone, password))
            self.connection.commit()
            return cursor.lastrowid
        except Error as exc:
            dlog.dlog_e(exc)
            return False

    def update_user(self, user_id: int, role: str, username: str, phone: str, password: str) -> bool:
        query = """
        UPDATE user
        SET role = %s, username = %s, phone = %s, password = %s, updated_at = NOW()
        WHERE id = %s
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (role, username, phone, password, user_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as exc:
            dlog.dlog_e(exc)
            return False
