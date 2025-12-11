from fastapi import Depends, APIRouter, HTTPException, Form, Request

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from common_utils.dependencies.authen import verify_password, create_access_token, hash_password

import dlog
from dconfig import config_object
from services.user_service import get_user_by_username, create_user

router = APIRouter(
    prefix="/register",
    tags=["/register"]
)
templates = Jinja2Templates(directory=config_object.TEMPLATE_DIR)


@router.get("/web")
async def login_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "ws_url": "/register/"})


@router.post("/")
async def register(username: str = Form(...), password: str = Form(...), phone: str = Form(...),
                   role: str = Form("user")):
    # Kiểm tra xem người dùng đã tồn tại chưa
    user = get_user_by_username(username)
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Mã hóa mật khẩu trước khi lưu vào cơ sở dữ liệu
    hashed_password = hash_password(password)

    # Thêm người dùng vào cơ sở dữ liệu
    create_user(role=role, username=username, phone=phone, password=hashed_password)
    return RedirectResponse(url="/login", status_code=303)
