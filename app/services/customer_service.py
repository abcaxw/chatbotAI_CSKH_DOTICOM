from database.dao.milvus.customer_dao import CustomerDAO


def get_customer_id(platform, platform_customer_id):
    customer_dao = CustomerDAO()
    customer = customer_dao.get_customer_by_platform(platform=platform, platform_customer_id=platform_customer_id)
    if customer:
        user_id = customer[0]["id"]
    else:
        user_id = insert_customer(platform=platform, platform_customer_id=platform_customer_id)
    return user_id


def insert_customer(platform, platform_customer_id):
    customer_dao = CustomerDAO()
    data = {
        "platform": platform,
        "platform_customer_id": platform_customer_id,
        "created_at": customer_dao.create_time(),
        "vector": [0.0, 0.0]
    }
    user_id = customer_dao.insert_customer(data)
    return user_id
