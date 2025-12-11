import traceback
from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.templating import Jinja2Templates

import dlog
from dconfig import config_object
from object_models.db_obj import Category, PaginationData
from services.category_service import get_all_categories, insert_category, \
    delete_category_by_id, get_categories_by_pagination, get_category_by_id, update_category_by_id

router = APIRouter(
    prefix="/category",
    tags=["/category"]
)

templates = config_object.TEMPLATES


@router.get("/web")
async def get(request: Request, page: int = 1, q: str = ""):
    return templates.TemplateResponse("category/list.html", {
        "request": request,
        "ws_url": "/category_list/",
        "page": page,
        "query": q,
        "total_pages": 10,
        "now": datetime.now()
    })


@router.get("/add")
async def add(request: Request):
    return templates.TemplateResponse("category/add.html", {
        "request": request,
        "ws_url": "/add/",
        "now": datetime.now()})


@router.get("/edit/{id}")
async def edit(request: Request, id: str):
    try:
        # Lấy thông tin category từ database
        category = get_category_by_id(id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
            
        return templates.TemplateResponse("category/edit.html", {
            "request": request,
            "ws_url": "/edit/",
            "id": id,
            "category": category,
            "now": datetime.now()
        })
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.post("/get-categories")
async def get_categories():
    try:
        categories = get_all_categories()
        json_message = "Get categories successfully"
        dlog.dlog_i(json_message)
        return JSONResponse({"message": json_message, "data": categories}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.post("/get-categories-by-pagination")
async def get_categories(pagination_data: PaginationData):
    try:
        categories, total_pages = get_categories_by_pagination(pagination_data)
        json_message = "Get categories successfully"
        dlog.dlog_i(json_message)
        data = {
            "categories": categories,
            "total_pages": total_pages
        }
        return JSONResponse({"message": json_message, "data": data}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.post("/add")
async def add_category(category: Category):
    try:
        new_category = Category(name=category.name, status=category.status)
        insert_category(new_category)
        return JSONResponse({"message": "Insert category successfully"}, status_code=200)
    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.delete("/delete/{category_id}")
async def delete_category(category_id: int):
    try:
        delete_category_by_id(category_id)
        return JSONResponse({"message": "Delete category successfully"}, status_code=200)
    except Exception as e:
        dlog.dlog_e(e)
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.get("/{category_id}")
async def get_category_by_category_id(category_id: int):
    try:
        category = get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        json_message = f"get category by id {category_id} successfully"
        dlog.dlog_i(json_message)
        return JSONResponse({"message": json_message, "data": category}, status_code=200)
    except Exception as e:
        dlog.dlog_e(f'Something wrong: {str(e)}')
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)


@router.put("/update-category/{category_id}")
async def update_document(category_id: str, category: Category):
    try:
        # Kiểm tra category tồn tại
        existing_category = get_category_by_id(category_id)
        if not existing_category:
            raise HTTPException(status_code=404, detail="Category not found")
            
        # Cập nhật cả name và status
        update_category_by_id(category_id, category.name, category.status)
        dlog.dlog_i(f"update category by id {category_id} successfully")
        return JSONResponse({"message": "Update category successfully"}, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        dlog.dlog_e(e)
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Something wrong"}, status_code=500)
