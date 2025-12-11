from starlette.templating import Jinja2Templates
from fastapi import APIRouter, Response

from dconfig import config_object

router = APIRouter(
    prefix="/logout",
    tags=["/logout"],
    redirect_slashes=False

)
templates = Jinja2Templates(directory=config_object.TEMPLATE_DIR)


@router.post("")
@router.post("/")
async def logout():
    response = Response(status_code=200)  # Mã 204 sẽ không có nội dung trả về
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="user_id")
    return response
