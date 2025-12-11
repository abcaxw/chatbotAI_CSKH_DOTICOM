from database.dao.mysql.user_dao import UserDAO


def get_user_by_username(username: str):
    user_dao = UserDAO()
    return user_dao.get_user_by_username(username)


def create_user(role: str, username: str, phone: str, password: str):
    user_dao = UserDAO()
    user_dao.insert_user(role, username, phone, password)
