import traceback

from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse

import dlog
from common_utils.dependencies.authen import auth_secret_key
from object_models.db_obj import QuestionDataData
from services.chat_service import chat

router = APIRouter(
    prefix="/chatbot",
    tags=["/chatbot"],
    dependencies=[Depends(auth_secret_key)]
)


@router.post("/chat")
def chatweb(data: QuestionDataData):
    try:
        bot_response, _, _ = chat(data.question, data.platform, data.user_id)
        json_message = "Chatbot đã trả lời"
        ai_message = bot_response.get('ai_message')
        return JSONResponse({"message": json_message, "data": {"ai_message": ai_message}}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)
