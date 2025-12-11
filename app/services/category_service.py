import math

from database.dao.mysql.category_dao import CategoryDAO


def get_categories_by_pagination(pagination_data):
    category_dao = CategoryDAO()
    categories, total_categories = category_dao.get_categories_by_pagination(pagination_data)
    total_pages = math.ceil(total_categories / pagination_data.page_size)
    return categories, total_pages

def get_all_categories():
    category_dao = CategoryDAO()
    categories = category_dao.get_all_categories()

    return categories


def insert_category(category):
    category_dao = CategoryDAO()
    return category_dao.insert_category(category)


def delete_category_by_id(category_id):
    category_dao = CategoryDAO()
    return category_dao.delete_category_by_id(category_id)

def get_category_by_id(category_id):
    category_dao = CategoryDAO()
    category = category_dao.get_category_by_id(category_id)
    return category

def update_category_by_id(category_id , name, status=None):
    category_dao = CategoryDAO()
    category_dao.update_category_by_id(int(category_id), name)