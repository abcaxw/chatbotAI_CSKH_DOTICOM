import json

from common_utils.string_utils import tach_chuoi_theo_url
from services import team_agent
from services.message_service import insert_message, get_messages_by_thread

from services.thread_chat_service import get_thread_id
from dconfig import config_object

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, ToolMessage, messages_from_dict

import dlog
from services.customer_service import get_customer_id


def chat(message, platform, platform_customer_id, message_id=None, reply_to_mid=None):
    try:
        customer_id = get_customer_id(platform=platform, platform_customer_id=platform_customer_id)
        thread_id = get_thread_id(platform=platform, platform_customer_id=platform_customer_id)
        list_chat_history, _, reply_to_info_message = get_messages_by_thread(thread_id=thread_id, page_number=1,
                                                      page_size=config_object.HISTORY_MESSAGES_NUMB,
                                                      reply_to_mid=reply_to_mid, sort_type="desc")
        chat_history = get_messages_history(list_chat_history, message, reply_to_info_message)
        insert_message(messages=[message], message_type="text", message_source="user",
                       thread_id=thread_id, customer_id=customer_id, platform=platform,
                       platform_message_ids=[message_id])
        bot_response = team_agent.process(message=message, history=chat_history.messages,
                                          thread_id=thread_id, customer=customer_id)

        bot_message = bot_response["ai_message"]
        messages = tach_chuoi_theo_url(bot_message)
        bot_response["bot_messages"] = messages
        dlog.dlog_i(f"AI chat: {bot_message}")

        platform_message_id = insert_message(messages=messages, message_type="text", message_source="chatbot",
                                    thread_id=thread_id, customer_id=customer_id, platform=platform,
                                    platform_message_ids=[])

        return bot_response, platform_message_id, thread_id
    except Exception as exc:
        dlog.dlog_e(exc)


# def get_all_chat_history(page_number, page_size, from_date, to_date, sort_type):
#     try:
#         from_date = convert_string_to_datetime(from_date)
#         to_date = convert_string_to_datetime(to_date)
#         message_dao = MessageDAO()
#         messages, total_pages = message_dao.get_all_messages(page_number=page_number,
#                                                              page_size=page_size,
#                                                              from_date=from_date,
#                                                              to_date=to_date,
#                                                              sort_type=sort_type)
#         return messages, total_pages
#     except Exception as exc:
#         dlog.dlog_e(exc)


# def chat_history_to_response(messages, page_number, page_size, total_pages, sort_type):
#     if sort_type == "desc":
#         suggestions = messages[0]["bot_recommendation"]
#
#     else:
#         suggestions = messages[-1]["bot_recommendation"]
#
#     chat_content = [
#         {
#             "chatId": message["_id"],
#             "question": message["user_message"],
#             "answer": message["bot_message"],
#             "url": message["bot_url"],
#             "createdTime": message["created_at"]
#         }
#         for message in messages
#     ]
#
#     data = {
#         "pageNumber": page_number,
#         "pageSize": page_size,
#         "totalPages": total_pages,
#         "thread_id": messages[0]["thread_id"],
#         "suggestions": suggestions,
#         "chatContent": chat_content
#     }
#     return data


def get_messages_history(list_chat_history, current_message, reply_to_info_message=None):
    messages = ChatMessageHistory()
    if list_chat_history:
        for message in list_chat_history:
            # Add user message first
            if message.get('message_source') == 'user':
                messages.add_user_message(message['messages'][-1])
            elif message.get('message_source') == 'chatbot':
                messages.add_ai_message(" ".join(message['messages']))
    if reply_to_info_message is None:
        messages.add_user_message(current_message)
    else:
        messages.add_user_message(f"{reply_to_info_message} reply to: {current_message}")
    return messages


def get_tool_messages(messages):
    tool_messages = []
    for message in messages:
        if message.type == "tool":
            tool_messages.append(message.content)
    return tool_messages


def chat_history_all_to_response(messages, page_number, page_size, total_pages):
    for message in messages:
        del message['converted_date']

    data = {
        "pageNumber": page_number,
        "pageSize": page_size,
        "totalPages": total_pages,
        "chatContent": messages
    }
    return data
