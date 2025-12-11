import os
import traceback
from typing import Optional, List
from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from common_utils.dependencies.authen import get_current_user
import dlog
from common_utils.file_utils import save_fastapi_request_file

from dconfig import config_object
from object_models.db_obj import CakeData
from services.cake_service import insert_cake, get_all_cakes, get_cake_by_id, update_cake, delete_cake, insert_cake_file

router = APIRouter(
    prefix="/cake",
    tags=["/cake"],
    dependencies=[Depends(get_current_user)]
)

# Cấu hình templates
templates = Jinja2Templates(directory=config_object.TEMPLATE_DIR)


@router.get("/web")
async def get(request: Request, page: int = 1, q: str = "", category: str = None, price: str = None, source: str = None):
    # Lấy tổng số bánh để tính số trang
    cakes, total_cakes = get_all_cakes(page=page, limit=8, search_query=q, form_filter=category, price_filter=price, source_filter=source)
    total_pages = (total_cakes + 7) // 8  # Mỗi trang 8 bánh

    return templates.TemplateResponse("cake/list.html", {
        "request": request,
        "cakes": cakes,
        "page": page,
        "query": q,
        "category": category or "",
        "price": price or "",
        "source_filter": source or "",
        "total_pages": total_pages,
        "now": datetime.now()
    })


@router.get("/add", name="cake.get", response_class=HTMLResponse)
async def add(request: Request):
    return templates.TemplateResponse("cake/add.html", {
        "request": request,
        "now": datetime.now()
    })


@router.get("/edit/{cake_id}")
async def edit(request: Request, cake_id: str):
    cake = get_cake_by_id(int(cake_id))
    if not cake:
        raise HTTPException(status_code=404, detail="Bánh không tồn tại")

    # Đảm bảo dữ liệu price và form được xử lý đúng
    if not cake.get('prices'):
        cake['prices'] = []
    if not cake.get('form'):
        cake['form'] = []

    # Tạo cặp price và form để template hiển thị dễ dàng
    # Đảm bảo rằng price và form có cùng độ dài
    prices = cake.get('prices', [])
    forms = cake.get('form', [])

    # Debug thông tin
    dlog.dlog_i(f"Cake data before template: id={cake_id}, source={cake.get('source')}, price={prices}, form={forms}")

    min_len = min(len(prices), len(forms))
    if min_len == 0:
        # Nếu không có dữ liệu, tạo một cặp mặc định
        cake['prices_forms'] = [(0, '')]
    else:
        # Chỉ sử dụng số lượng phần tử bằng nhau từ cả hai mảng
        cake['prices_forms'] = list(zip(prices[:min_len], forms[:min_len]))

    dlog.dlog_i(f"Processed prices_forms for template: {cake['prices_forms']}")

    # Thêm hàm zip vào context
    return templates.TemplateResponse("cake/edit.html", {
        "request": request,
        "cake": cake,
        "now": datetime.now(),
        "zip": zip  # Thêm hàm zip Python vào template context
    })


@router.post("/add-cake")
async def add_cake(cake_data: CakeData):
    try:
        cake_id = insert_cake(cake_data)
        data = {
            "id": cake_id,
            "name": cake_data.name
        }
        return JSONResponse({"message": "Thêm bánh thành công", "data": data}, status_code=200)

    except Exception as e:
        dlog.dlog_e(e)
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Có lỗi xảy ra khi thêm bánh"}, status_code=500)


@router.put("/edit/{cake_id}")
async def edit_cake(cake_id: str,
                    name: str = Form(...),
                    description: str = Form(...),
                    source: str = Form(...),
                    prices: Optional[list[float]] = Form(None),
                    form: Optional[list[str]] = Form(None)):
    try:
        # Lấy bánh hiện tại để kiểm tra
        existing_cake = get_cake_by_id(int(cake_id))
        if not existing_cake:
            raise HTTPException(status_code=404, detail="Không tìm thấy bánh")

        # Tạo đối tượng CakeData với dữ liệu mới
        cake_data = CakeData(
            name=name,
            description=description,
            prices=prices,
            form=form,
            source=source,
            image_url=existing_cake.get('image_url', 'temp')
        )

        success = update_cake(int(cake_id), cake_data)

        if not success:
            raise HTTPException(status_code=500, detail="Cập nhật bánh không thành công")

        return JSONResponse({"message": "Cập nhật bánh thành công"}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        dlog.dlog_e(f"Error updating cake: {str(e)}")
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": f"Có lỗi xảy ra khi cập nhật bánh: {str(e)}"},
                            status_code=500)


@router.delete("/delete/{cake_id}")
async def remove_cake(cake_id: str):
    try:
        success = delete_cake(cake_id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy bánh")

        return JSONResponse({"message": "Xóa bánh thành công"}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        dlog.dlog_e(e)
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": "Có lỗi xảy ra khi xóa bánh"}, status_code=500)


@router.post("/add-file")
async def add_cake(file: UploadFile = File(None),
                   name: str = Form(...),
                   description: str = Form(...),
                   source: str = Form(...),
                   prices: Optional[list[float]] = Form(None),
                   form: Optional[list[str]] = Form(None)):
    try:
        path_file = None
        if file is not None:
            if file.size != 0:
                path_file = save_fastapi_request_file(file)

        # Log thông tin nhận được để debug
        dlog.dlog_i(f"Received cake data: name={name}, source={source}, prices={prices}, form={form}")

        cake = CakeData(name=name, description=description, prices=prices,
                        image_url="temp", form=form, source=source)
        cake_id = insert_cake_file(path_file, cake)
        data = {
            "cake_id": cake_id
        }
        return JSONResponse({"message": "insert document successfully", "data": data}, status_code=200)

    except Exception as e:
        dlog.dlog_e(f"Error adding cake: {str(e)}")
        traceback.print_exc()
        raise HTTPException(detail={"error": 1, "message": f"Something wrong: {str(e)}"}, status_code=500)
