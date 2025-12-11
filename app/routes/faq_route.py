import traceback
from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.templating import Jinja2Templates

from common_utils.dependencies.authen import auth_secret_key
from fastapi.responses import HTMLResponse
import dlog
from dconfig import config_object
from object_models.db_obj import PaginationData, Faq, FaqPaginationData
from services.faq_service import faqs_to_response, get_faqs_by_pagination, insert_faqs, delete_faq_by_id, \
    update_faq_by_id, update_faq_by_question, delete_faq_by_question, get_faq_by_id

router = APIRouter(
    prefix="/faq",
    tags=["/faq"],
    # dependencies=[Depends(auth_secret_key)]
)
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/web")
async def get(request: Request, page: int = 1, q: str = ""):
    return templates.TemplateResponse("faq/list.html", {
        "request": request,
        "ws_url": "/faq_manager/",
        "page": page,
        "query": q,
        "total_pages": 10,
        "now": datetime.now()
    })


@router.get("/edit/{id}")
async def edit(request: Request, id: str):
    return templates.TemplateResponse("faq/edit.html", {
        "request": request,
        "ws_url": "/edit/",
        "id": id
    })


@router.get("/add", name="faq.get" ,response_class=HTMLResponse)  # Thêm route cho /faq/add và phục vụ add_faq.html
async def add_faq_page(request: Request):
    return templates.TemplateResponse("faq/add.html", {
        "request": request,
        "ws_url": "/add_faq/",
        "now": datetime.now()
    })


@router.post("/get_faqs")
async def get_faq(data: FaqPaginationData):
    try:
        faqs, total_pages = get_faqs_by_pagination(page_number=data.page_number,
                                                   page_size=data.page_size, sort_type=data.sort,
                                                   title=data.title, question=data.question)
        json_message = "Get get faqs successfully"

        if not faqs:
            return JSONResponse({"message": json_message, "data": {}}, status_code=200)

        faqs_data = faqs_to_response(faqs, data.page_number, data.page_size, total_pages)
        dlog.dlog_i(f"get faqs successfully")
        return JSONResponse({"message": json_message, "data": faqs_data}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.put("/update_faq_by_id")
async def update_faq(faq_id: str, faq: Faq):
    try:
        update_faq_by_id(faq_id, faq)
        dlog.dlog_e(f"update faq by id {faq_id} successfully")
        return JSONResponse({"message": "update faq successfully"}, status_code=200)

    except Exception as e:
        dlog.dlog_e(e)
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.put("/update_faq_by_question")
async def update_faq(faq: Faq):
    try:
        update_faq_by_question(faq)
        dlog.dlog_e(f"update faq by question {faq.question} successfully")
        return JSONResponse({"message": "update faq successfully"}, status_code=200)

    except Exception as e:
        dlog.dlog_e(e)
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.delete("/delete_faq_by_id")
async def delete_faq(faq_id: str):
    try:
        deleted_count = delete_faq_by_id(faq_id)
        data = {"deleted_count": deleted_count}
        dlog.dlog_i(f"delete faq successfully id {faq_id}")
        return JSONResponse({"message": "Delete successfully", "data": data}, status_code=200)
    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.delete("/delete_faq_by_question")
async def delete_faq(question: str):
    try:
        deleted_count = delete_faq_by_question(question)
        dlog.dlog_e(f"delete faq successfully question {question}")
        return JSONResponse({"message": "Delete successfully", "data": {"deleted_count": deleted_count}},
                            status_code=200)
    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.post("/add_faqs")
async def add_faqs(faqs: list[Faq]):
    try:
        insert_faqs(faqs)

        return JSONResponse({"message": "insert faq successfully"}, status_code=200)

    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.get("/{faq_id}")
async def get_faq_by_faq_id(faq_id: int):
    try:
        faq = get_faq_by_id(faq_id)
        if not faq:
            raise HTTPException(status_code=404, detail="Document not found")
        json_message = f"get document by id {faq_id} successfully"
        dlog.dlog_i(json_message)
        return JSONResponse({"message": json_message, "data": faq}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)
