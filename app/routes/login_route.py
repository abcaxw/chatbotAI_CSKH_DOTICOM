from fastapi import APIRouter, HTTPException, Form, Request

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from common_utils.dependencies.authen import verify_password, create_access_token
from dconfig import config_object

from services.user_service import get_user_by_username

router = APIRouter(
    prefix="/login",
    tags=["/login"]
)
templates = Jinja2Templates(directory=config_object.TEMPLATE_DIR)


@router.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "ws_url": "/login/"})


@router.post("/")
async def login(username: str = Form(...), password: str = Form(...)):
    user = get_user_by_username(username)
    if user and verify_password(password, user["password"]):
        access_token = create_access_token({"sub": username})
        response = RedirectResponse(url="/document/web", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}")
        response.set_cookie(key="user_id", value=user["id"])
        return response
    raise HTTPException(status_code=401, detail="Invalid credentials")
