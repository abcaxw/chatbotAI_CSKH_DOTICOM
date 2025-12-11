import traceback

from fastapi import APIRouter, HTTPException, Request, Query, BackgroundTasks
from fastapi.responses import JSONResponse

import dconfig
import dlog

from services.meta_service import handle_events_from_message, is_valid_signature

router = APIRouter(
    prefix="/chatbot_meta",
    tags=["/chatbot_meta"],
)


@router.get("/webhook")
async def verify_token(hub_mode: str = Query(None, alias="hub.mode"),
                       hub_challenge: str = Query(None, alias="hub.challenge"),
                       hub_verify_token: str = Query(None, alias="hub.verify_token")):
    if hub_mode == "subscribe" and hub_verify_token == dconfig.config_object.PAGE_FACEBOOK_ACCESS_TOKEN:
        dlog.dlog_i(f"{hub_challenge}")
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch")


@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        signature = request.headers.get('x-hub-signature')
        body = await request.body()
        if not is_valid_signature(body, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

        data = await request.json()
        # Handle the events from Messenger
        background_tasks.add_task(handle_events_from_message, data)

        return JSONResponse({"message": "Chat successfully"}, status_code=200)

    except Exception as e:
        dlog.dlog_e(f'System error: {str(e)}')
        traceback.print_exc()
        return JSONResponse({"message": "Chat unsuccessfully"}, status_code=200)
