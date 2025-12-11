from database.dao.milvus.thread_dao import ThreadDAO


def insert_thread_id(platform, platform_customer_id):
    thread_dao = ThreadDAO()
    data = {"user_id": platform_customer_id,
            "platform": platform,
            "created_at": thread_dao.create_time(),
            "vector": [0.0, 0.0]
            }
    thread_id = thread_dao.insert_thread(data)
    return thread_id


def get_thread_id(platform, platform_customer_id):
    thread_dao = ThreadDAO()
    thread = thread_dao.get_thread(platform, platform_customer_id)

    if thread:
        thread_id = thread[0]["id"]
    else:
        thread_id = insert_thread_id(platform, platform_customer_id)
    return thread_id
