import time
import re

from database.dao.milvus.message_dao import MessageDAO
from services.chat_service import chat
from dconfig import config_object

import requests
import json
import hashlib
import hmac
import dlog

dict_user_not_use_chatbot_facebook = {}


def handle_events_from_message(data, persona_id_chatbot=config_object.PERSONA_ID_CHATBOT_FACEBOOK):
    for entry in data.get('entry', []):
        if entry.get('messaging'):
            handle_user_send_message(entry, persona_id_chatbot)

        if entry.get("standby"):
            handle_admin_send_message(entry)


def handle_send_messages(persona_id_chatbot, sender_id, bot_message, message_id, quick_reply_texts=None):
    message_content = {
        "text": bot_message,
        "message_type": "text",
    }
    quick_replies = get_quick_replies(quick_reply_texts)

    payload_message = get_payload_message(psid=sender_id, message_content=message_content, quick_replies=quick_replies)
    message_id = send_facebook_message(persona_id=persona_id_chatbot, payload=payload_message, message_id=message_id)

    return message_id


def handle_send_messages_with_attachment(persona_id_chatbot, sender_id, attachment_id, message_id):
    payload = {
        "recipient": {
            "id": sender_id,
        },
        "message": {
            "attachment": {
                "type": "audio",  # Adjust to the correct type (e.g., "video" or "file")
                "payload": {
                    "attachment_id": attachment_id,
                }
            },
            "metadata": "CHATBOT_SEND_MESSAGE"

        }
    }
    send_facebook_message(persona_id=persona_id_chatbot, payload=payload, message_id=message_id)


def handle_send_messages_with_button_url(persona_id_chatbot, sender_id, bot_message, message_id, url):
    message_content = {
        "text": bot_message,
        "message_type": "button",
        "url": url,
        "suggestion_questions": None
    }
    payload_message = get_payload_button(psid=sender_id, message_content=message_content)
    send_facebook_message(persona_id=persona_id_chatbot, payload=payload_message, message_id=message_id)


def handle_send_suggestion(persona_id_chatbot, sender_id, bot_recommendations):
    message_content_suggestion = {
        "text": "Quý khách có thể quan tâm:",
        "message_type": "generic",
        "suggestion_questions": bot_recommendations
    }
    payload_suggestion = get_payload_generic(sender_id, message_content_suggestion)
    send_facebook_message(persona_id=persona_id_chatbot, payload=payload_suggestion)


def send_facebook_message(persona_id: str, payload, message_id=None):
    url = f"{config_object.GRAPH_FACEBOOK_DOMAIN}/v16.0/me/messages"
    headers = {"Content-Type": "application/json"}
    params = {
        "access_token": config_object.PAGE_FACEBOOK_ACCESS_TOKEN,
        "persona_id": persona_id
    }

    response = requests.post(url, json=payload, headers=headers, params=params)

    data = response.json()
    if response.status_code != 200:
        dlog.dlog_e(f"Send message in platform facebook not success")
        # raise HTTPException(status_code=response.status_code, detail=response.text)
        return
    if message_id:  # set save message id in platform
        platform_message_id = data["message_id"]
        message_dao = MessageDAO()
        message_id = message_dao.update_platform_message_id(message_id=message_id,
                                                            platform_message_id=platform_message_id)
    dlog.dlog_i(f"successfully send message to messenger")
    return message_id


def upload_facebook_attachment(file_path):
    url = f"{config_object.GRAPH_FACEBOOK_DOMAIN}/v21.0/me/message_attachments?access_token={config_object.PAGE_FACEBOOK_ACCESS_TOKEN}"

    payload = json.dumps({
        "message": {
            "attachment": {
                "type": "audio"
            }
        },
        "filedata": file_path,
        "type": "audio/3gpp"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.json())

    if response.status_code != 200:
        dlog.dlog_e(f"Send message in platform facebook not success")
        # raise HTTPException(status_code=response.status_code, detail=response.text)
        return None
    # TODO: co can add voice vao log ko
    # if message_id:  # set save message id in platform
    #     platform_message_id = data["message_id"]
    #     message_dao = MessageDAO()
    #     message_dao.update_platform_message_id(message_id=message_id, platform_message_id=platform_message_id)
    dlog.dlog_i(f"successfully upload file to messenger")
    data = response.json()
    attachment_id = data['attachment_id']
    return attachment_id


def get_button_url_template(url, title="Thông tin tham khảo"):
    button_data = {
        "type": "web_url",
        "url": url,
        "title": title
    }
    return [button_data]


def get_button_template(questions=None):
    if questions is None:
        questions = config_object.RECOMMEND_QUESTIONS
    button_data = [
        {
            "type": "postback",
            "title": question,
            "payload": question
        }
        for question in questions
    ]
    return button_data


def get_generic_template(questions=None):
    if questions is None:
        questions = config_object.RECOMMEND_QUESTIONS
    generic_data = [
        {
            "title": question,
            "buttons": [
                {
                    "type": "postback",
                    "title": f"Xem chi tiết",
                    "payload": question
                }]
        }
        for idx, question in enumerate(questions)
    ]

    return generic_data


def get_payload_generic(psid, message_content):
    payload = {
        'recipient': {'id': psid},
        'message': {
            "attachment": {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': get_generic_template(message_content["suggestion_questions"])
                }
            },
            "metadata": "CHATBOT_SEND_MESSAGE"
        }
    }

    return payload


def get_payload_button(psid, message_content):
    payload = {
        'recipient': {'id': psid},
        'message': {
            "attachment": {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': message_content['text'],  # The message text
                    'buttons': []  # List of buttons
                }
            },
            "metadata": "CHATBOT_SEND_MESSAGE"
        }
    }
    if message_content["url"]:
        payload["message"]["attachment"]["payload"]["buttons"] = get_button_url_template(url=message_content["url"])
    if message_content["suggestion_questions"]:
        payload["message"]["attachment"]["payload"]["buttons"].extend(
            get_button_template(message_content["suggestion_questions"]))  # List of buttons
    return payload


def get_payload_image(psid, message_content):
    payload = {
        'recipient': {'id': psid},
        'message': {
            "attachment": {
                'type': 'image',
                'payload': {
                    'url': message_content["image"],  # Direct URL to the image
                    'is_reusable': True
                }
            },
            "metadata": "CHATBOT_SEND_MESSAGE"
        }

    }
    return payload


def get_quick_replies(quick_reply_texts):
    quick_replies = None
    if quick_reply_texts:
        quick_replies = [
            {
                "content_type": "text",
                "title": text,
                "payload": text
            }
            for i, text in enumerate(quick_reply_texts)
        ]

    return quick_replies


def get_payload_message(psid, message_content, quick_replies=None):
    payload = {
        'recipient': {'id': psid},
        'message': {
            "text": message_content["text"],
            "metadata": "CHATBOT_SEND_MESSAGE"
        }
    }
    if quick_replies:
        payload['message']["quick_replies"] = quick_replies

    return payload


def set_sender_action(psid, persona_id, sender_action='typing_off'):
    url = f"{config_object.GRAPH_FACEBOOK_DOMAIN}/v16.0/me/messages"
    headers = {"Content-Type": "application/json"}
    params = {
        "access_token": config_object.PAGE_FACEBOOK_ACCESS_TOKEN
    }
    payload = {
        'recipient': {'id': psid},
        "sender_action": sender_action,
        "persona_id": persona_id
    }
    response = requests.post(url, headers=headers, json=payload, params=params)
    return response.json()


def get_user_info(recipient_id):
    url = f"{config_object.GRAPH_FACEBOOK_DOMAIN}/{recipient_id}"
    params = {
        "fields": "name,first_name,last_name,profile_pic",
        "access_token": config_object.PAGE_FACEBOOK_ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    return response.json()


def set_get_start_message(message_default):
    url = f"{config_object.GRAPH_FACEBOOK_DOMAIN}/v16.0/me/messenger_profile"
    params = {
        "access_token": config_object.PAGE_FACEBOOK_ACCESS_TOKEN
    }
    greeting = [
        {
            "locale": "default",
            "text": message_default
        }]
    payload = {
        "greeting": greeting
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload, params=params)

    return response.json()


def is_valid_signature(payload, signature):
    """Verify the request signature using the app secret."""
    if not signature:
        return False

    hash_type, signature_hash = signature.split('=')
    expected_hash = hmac.new(
        config_object.APP_SECRET_FACEBOOK.encode(), payload, hashlib.sha1
    ).hexdigest()

    return hmac.compare_digest(signature_hash, expected_hash)


# def handle_process_reaction_feedback(reaction_data, sender_id, persona_id_chatbot):
#     emoji_icons = {
#         b"\xe2\x9d\xa4": {"des": "heart", "rating": 1},
#         b"\xf0\x9f\x98\x86": {"des": "laugh", "rating": 1},
#         b"\xf0\x9f\x98\xae": {"des": "wow", "rating": 1},
#         b"\xf0\x9f\x98\xa2": {"des": "sad", "rating": 0},
#         b"\xf0\x9f\x98\xa1": {"des": "angry", "rating": 0},
#         b"\xf0\x9f\x91\x8d": {"des": "like", "rating": 1},
#         b"\xf0\x9f\x91\x8e": {"des": "unlike", "rating": 0},
#         b"\xf0\x9f\x98\x8d": {"des": "love", "rating": 1},
#         b"\xf0\x9f\xa5\xb0": {"des": "love love", "rating": 1},
#         b"\xf0\x9f\x98\x98": {"des": "kiss heart", "rating": 1},
#         b"\xf0\x9f\xa4\xa9": {"des": "star eyes", "rating": 1},
#     }
#     platform_message_id = reaction_data["mid"]
#     action = reaction_data["action"]
#     if action == "react":
#         emoji = reaction_data.get("emoji")
#         emoji_encode = emoji.encode("utf-8")
#         if emoji_encode in emoji_icons.keys():
#             rating = emoji_icons[emoji_encode]["rating"]
#             send_rating_kafka_other_platform(platform="facebook",
#                                              platform_customer_id=sender_id,
#                                              platform_message_id=platform_message_id,
#                                              rating=rating)
#             dlog.dlog_i("Process successfully reaction facebook")
#             if rating == 0:
#                 handle_send_messages(persona_id_chatbot, sender_id, config_object.THANKS, message_id=None)


def handle_admin_send_message(entry):
    global dict_user_not_use_chatbot_facebook

    for event in entry.get('standby', []):
        sender_id = event['sender']['id']
        recipient_id = event['recipient']['id']
        if sender_id == config_object.PAGE_FACEBOOK_APP_ID:
            message = event['message']
            check_admin_send_attachments(message, recipient_id)


def reset_user_not_use_chatbot_facebook():
    global dict_user_not_use_chatbot_facebook
    dict_user_not_use_chatbot_facebook = {}


def handle_user_send_message(entry, persona_id_chatbot, platform="facebook"):
    global dict_user_not_use_chatbot_facebook
    for event in entry.get('messaging', []):
        sender_id = event['sender']['id']
        recipient_id = event['recipient']['id']
        if sender_id in dict_user_not_use_chatbot_facebook.keys():
            continue
        event_keys = event.keys()
        payload_data = None
        message_text = None
        voice_answer = False
        reply_to_mid = None
        facebook_message_id = None
        if "message" in event_keys:
            message = event['message']
            facebook_message_id = message['mid']
            reply_to = message.get('reply_to')
            if reply_to:
                reply_to_mid = reply_to.get("mid")
            if check_admin_message(message, recipient_id):
                continue
            # TODO: clean up later
            message_text, voice_answer = get_attachments(message)

            if message.get("quick_reply"):
                quick_reply_data = message.get("quick_reply")
                payload_data = quick_reply_data.get("payload")
        if "postback" in event_keys:
            postback = event.get("postback")
            payload_data = postback.get("payload")
        if payload_data:
            message_text = payload_data
        # if "reaction" in event_keys:
        #     reaction = event.get("reaction")
        #     handle_process_reaction_feedback(reaction, sender_id, persona_id_chatbot)
        #     continue

        if message_text:

            set_sender_action(sender_id, persona_id_chatbot, sender_action='TYPING_ON')
            bot_response, message_id, _ = chat(message=message_text, platform_customer_id=sender_id, platform=platform,
                                               reply_to_mid=reply_to_mid, message_id=facebook_message_id)
            bot_messages = bot_response["bot_messages"]
            bot_recommendations = bot_response.get("recommendation_questions")
            # send message text to user
            url = bot_response.get("url")
            # TODO: clean up
            quick_reply_texts = None
            for message in bot_messages:
                if message.startswith("https://"):
                    message_id = send_image_by_url(sender_id, message, message_id)
                else:
                    message_id = handle_send_messages(persona_id_chatbot, sender_id, message, message_id,
                                                      quick_reply_texts)
            set_sender_action(sender_id, persona_id_chatbot)


def check_admin_message(message, recipient_id):
    if message.get("is_echo"):
        if message.get("metadata") == "CHATBOT_SEND_MESSAGE":
            return True
        check_admin_send_attachments(message, recipient_id)
        return True
    return False


def check_admin_send_attachments(message, recipient_id):
    global dict_user_not_use_chatbot_facebook
    if recipient_id not in dict_user_not_use_chatbot_facebook.keys():
        dict_user_not_use_chatbot_facebook[recipient_id] = {"last_time": time.time()}
    message_text = message.get("text")
    if not message_text:
        attachments = message.get("attachments")
        for attachment in attachments:
            attachment_title = attachment.get("title")
            attachment_title_trimmed = attachment_title[:-3]
            if config_object.TEXT_FEEDBACK_FROM_OC_ZALO.startswith(attachment_title_trimmed) \
                    and recipient_id in dict_user_not_use_chatbot_facebook.keys():
                del dict_user_not_use_chatbot_facebook[recipient_id]
                break


def get_attachments(message):
    message_text = message.get("text")
    voice_answer = False
    if message.get("attachments"):
        for file in message.get("attachments"):
            if file.get("type") in ['video', 'image']:
                url = file.get("payload").get("url")
                # message_text = f"{file.get('type')}: {url}"
                message_text = url
            if file.get("type") == 'audio':
                # TODO : update process voice
                pass
                # url = file.get("payload").get("url")
                # transcript = platform_voice_record_to_text(url, platform)
                # message_text = transcript
                # voice_answer = True
    return message_text, voice_answer


def send_image_by_url(recipient_id, image_url, message_id):
    """Gửi ảnh bằng URL."""
    params = {
        "access_token": config_object.PAGE_FACEBOOK_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url,
                    "is_reusable": True
                }
            },
            "metadata": "CHATBOT_SEND_MESSAGE"
        }

    }
    response = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
    data_response = response.json()
    dlog.dlog_i(f"Đã gửi ảnh thành công: {response.json()}")
    if response.status_code == 200:  # set save message id in platform
        platform_message_id = data_response["message_id"]
        message_dao = MessageDAO()
        message_id = message_dao.update_platform_message_id(message_id=message_id,
                                                            platform_message_id=platform_message_id)
    return message_id

