from typing import Union

from fastapi import Query, HTTPException
from starlette.websockets import WebSocket


# from object_model.actions_cfg import ActionsCfg


async def get_token(
        websocket: WebSocket,
        token: Union[str, None] = Query(default=None)):
    if token is None:
        raise HTTPException(status_code=403, detail="Access Denied")
    return token
