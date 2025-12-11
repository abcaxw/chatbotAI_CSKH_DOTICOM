from database.dao.milvus.message_dao import MessageDAO


def get_messages_by_thread(thread_id, page_number, page_size, sort_type, reply_to_mid=None):
    offset = (page_number - 1) * page_size
    limit = page_size
    message_dao = MessageDAO()
    filter = f"thread_id == {thread_id}"
    output_fields = ["*"]
    search_params = {
        "metric_type": "IP",
        # highlight-next-line
        "offset": offset  # The records to skip
    }
    total_messages = message_dao.count_message(filter)
    record = message_dao.get_messages_by_filter(filter, output_fields, search_params, limit)
    reply_to_info_message = None
    if reply_to_mid:
        filter = f'ARRAY_CONTAINS_ANY(platform_message_ids, {[reply_to_mid]})'
        reply_to_info = message_dao.get_messages_by_filter(filter, output_fields, search_params, limit)
        if reply_to_info:
            reply_to_mid_index = reply_to_info[0]["platform_message_ids"].index(reply_to_mid)
            reply_to_info_message = reply_to_info[0]["messages"][reply_to_mid_index]
    return record, total_messages, reply_to_info_message


def insert_message(messages, message_type, message_source, thread_id, customer_id, platform, platform_message_ids):
    message_dao = MessageDAO()
    message = {
        "thread_id": thread_id,
        "customer_id": customer_id,
        "messages": messages,
        "message_type": message_type,
        "message_source": message_source,
        "platform": platform,
        "platform_message_ids": platform_message_ids,
        "created_at": message_dao.create_timestamp(),
        "vector": [0.0, 0.0]
    }
    result = message_dao.insert_message(message)
    message_id = result["ids"][-1]
    return message_id
