import time
from typing import Optional, Dict, Any

from PIL import Image
from google.api_core import retry
from google.generativeai.types import RequestOptions

import dlog
from coreAI import embedding_image_model, embedding_service
from coreAI.llm.gemini_llm import gemini_1_5_flash
from database.dao.milvus.cake_dao import CakeDAO
from database import minio_service

from dconfig import config_prompts


def insert_cake(cake_data):
    dlog.dlog_i(f"---INSERT cake {cake_data.name}")
    cake_dao = CakeDAO()

    # Kiểm tra nếu tên bánh đã tồn tại
    if cake_dao.find_image_by_name(cake_data.name):
        dlog.dlog_e(f"Cake with name {cake_data.name} already exists")
        return None

    cake_data.description = f"{cake_data.description} {cake_data.form}  Giá: {cake_data.price} VNĐ"

    # Tạo vector nhúng cho ảnh
    image_vector, image_path = embedding_image_model.get_embedding(cake_data.image_url)
    cake = cake_data.to_dict()

    # Tạo mô tả chi tiết cho bánh bằng mô hình AI
    image = Image.open(image_path)
    prompt = config_prompts.DESCRIPTION_IMAGE_PROMPT.format(description=cake_data.description)
    start_time = time.time()
    response = gemini_1_5_flash.generate_content(contents=[prompt, image], request_options=RequestOptions(
        retry=retry.Retry(initial=1, multiplier=1, maximum=60, timeout=100)))
    dlog.dlog_i(f"Process time description image: {time.time() - start_time}")

    cake["description"] = response.text

    # Thêm các vector nhúng
    cake["image_vector"] = image_vector
    description_vector = embedding_service.create_embedding(cake["description"])
    cake["description_vector"] = description_vector

    # Lưu vào cơ sở dữ liệu
    cake_id = cake_dao.insert_cakes([cake])

    return cake_id


def get_all_cakes(page: int = 1, limit: int = 8, search_query: str = "", form_filter: str = None,
                  price_filter: str = None, source_filter: str = None):
    """
    Lấy danh sách bánh theo trang và các bộ lọc
    
    Args:
        page: Số trang
        limit: Giới hạn số bánh trên một trang
        search_query: Từ khóa tìm kiếm
        form_filter: Lọc theo loại bánh
        price_filter: Lọc theo giá
        source_filter: Lọc theo nguồn
        
    Returns:
        Tuple gồm danh sách bánh và tổng số bánh
    """

    cake_dao = CakeDAO()
    offset = (page - 1) * limit

    # Tạo filter expression
    filter_expr = []

    # Lọc theo tên
    if search_query:
        filter_expr.append(f'name like "%{search_query}%"')

    # Lọc theo loại bánh
    if form_filter:
        filter_expr.append(f'form like "%{form_filter}%"')

    # Lọc theo nguồn
    if source_filter:
        filter_expr.append(f'source == "{source_filter}"')

    # Lọc theo giá
    if price_filter:
        if price_filter == "0-250000":
            filter_expr.append('price_max <= 250000')
        elif price_filter == "250000-500000":
            filter_expr.append('price_min > 250000 and price_max <= 500000')
        elif price_filter == "500000-1000000":
            filter_expr.append('price_min > 500000 and price_max <= 1000000')
        elif price_filter == "1000000+":
            filter_expr.append('price_max > 1000000')

    # Kết hợp các điều kiện
    query_expr = " and ".join(filter_expr) if filter_expr else ""

    # Thực hiện truy vấn
    cakes, total = cake_dao.get_cakes(offset=offset, limit=limit, expr=query_expr)

    # Xử lý dữ liệu
    result_cakes = []
    for cake in cakes:
        # Xử lý giá và loại bánh
        prices = cake.get('price', [])
        forms = cake.get('form', [])

        # Tạo phạm vi giá
        price_range = ""
        if prices:
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0

            if min_price == max_price:
                price_range = f"{min_price:,} VNĐ"
            else:
                price_range = f"{min_price:,} - {max_price:,} VNĐ"

        # Gắn thêm thông tin
        cake['price_range'] = price_range
        cake['category_name'] = forms[0] if forms else "Không xác định"

        result_cakes.append(cake)

    return result_cakes, total


def get_cake_by_id(cake_id: int) -> Optional[Dict[str, Any]]:
    """
    Lấy thông tin chi tiết của một bánh kem theo ID
    
    Args:
        cake_id: ID của bánh kem
        
    Returns:
        Thông tin bánh kem hoặc None nếu không tìm thấy
    """
    dlog.dlog_i(f"---GET cake by ID: {cake_id}")
    cake_dao = CakeDAO()
    return cake_dao.get_cake_by_id(cake_id)


def update_cake(cake_id: int, cake_data) -> bool:
    """
    Cập nhật thông tin bánh kem
    
    Args:
        cake_id: ID của bánh kem cần cập nhật
        cake_data: Dữ liệu bánh kem mới
        
    Returns:
        True nếu cập nhật thành công, False nếu không tìm thấy bánh
    """
    dlog.dlog_i(f"---UPDATE cake {cake_id}")
    cake_dao = CakeDAO()

    # Kiểm tra xem bánh có tồn tại không
    existing_cake = cake_dao.get_cake_by_id(cake_id)
    if not existing_cake:
        dlog.dlog_i(f"Cake with ID {cake_id} not found")
        return False

    # Chuẩn bị dữ liệu bánh mới
    cake_data.description = f"{cake_data.description} {cake_data.form}  Giá: {cake_data.prices} VNĐ"

    # Tạo vector nhúng mới nếu ảnh thay đổi
    image_vector = None
    image_path = None
    if cake_data.image_url != existing_cake.get("image_url"):
        image_vector, image_path = embedding_image_model.get_embedding(cake_data.image_url)
    else:
        # Sử dụng lại vector ảnh cũ
        image_vector = existing_cake.get("image_vector")

    # Chuẩn bị dữ liệu cập nhật
    cake = cake_data.to_dict()
    cake["id"] = int(cake_id)

    # Tạo mô tả mới nếu có ảnh mới
    if image_path:
        image = Image.open(image_path)
        prompt = config_prompts.DESCRIPTION_IMAGE_PROMPT.format(description=cake_data.description)
        start_time = time.time()
        response = gemini_1_5_flash.generate_content(contents=[prompt, image], request_options=RequestOptions(
            retry=retry.Retry(initial=1, multiplier=1, maximum=60, timeout=100)))
        dlog.dlog_i(f"Process time description image: {time.time() - start_time}")
        cake_data.description = response.text

    if cake_data.description != existing_cake.get("description"):
        cake["description"] = cake_data.description

    # Cập nhật vector
    cake["image_vector"] = image_vector
    description_vector = embedding_service.create_embedding(cake["description"])
    cake["description_vector"] = description_vector

    # Cập nhật trong cơ sở dữ liệu
    return cake_dao.update_cake(cake_id, cake)


def delete_cake(cake_id: str) -> bool:
    """
    Xóa bánh kem theo ID
    
    Args:
        cake_id: ID của bánh kem cần xóa
        
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy bánh
    """
    dlog.dlog_i(f"---DELETE cake {cake_id}")
    cake_dao = CakeDAO()

    # Kiểm tra xem bánh có tồn tại không
    existing_cake = cake_dao.get_cake_by_id(cake_id)
    if not existing_cake:
        dlog.dlog_i(f"Cake with ID {cake_id} not found")
        return False

    # Xóa bánh từ cơ sở dữ liệu
    return cake_dao.delete_cake(cake_id)


def insert_cake_file(file_path: str, cake_data) -> int:
    cake_dao = CakeDAO()

    # Kiểm tra nếu tên bánh đã tồn tại
    if cake_dao.find_image_by_name(cake_data.name):
        dlog.dlog_e(f"Cake with name {cake_data.name} already exists")
        return None

    cake_data.description = f"{cake_data.description} {cake_data.form}  Giá: {cake_data.price} VNĐ"

    # Tạo vector nhúng cho ảnh
    image_vector, _ = embedding_image_model.get_embedding(file_path)
    cake = cake_data.to_dict()

    # Tạo mô tả chi tiết cho bánh bằng mô hình AI
    image = Image.open(file_path)
    prompt = config_prompts.DESCRIPTION_IMAGE_PROMPT.format(description=cake_data.description)
    start_time = time.time()
    response = gemini_1_5_flash.generate_content(contents=[prompt, image], request_options=RequestOptions(
        retry=retry.Retry(initial=1, multiplier=1, maximum=60, timeout=100)))
    dlog.dlog_i(f"Process time description image: {time.time() - start_time}")

    cake["description"] = response.text

    # Thêm các vector nhúng
    cake["image_vector"] = image_vector
    description_vector = embedding_service.create_embedding(cake["description"])
    cake["description_vector"] = description_vector

    # minio_service.upload_file(file_path, f'uploads/{cake_data.name}', cake_data.source)
    # url = f"{config_object.DOMAIN_MINIO}/chatbot/uploads/{cake_data.name}"
    # cake_dao.image_url = url

    # Lưu vào cơ sở dữ liệu
    cake_id = cake_dao.insert_cakes([cake])

    return cake_id


def get_cakes_by_names(cake_names: list[str]):
    """
        Lấy thông tin chi tiết của nhiều bánh kem theo cake_names

        Args:
            cake_names: cake_name của bánh kem

        Returns:
            Thông tin bánh kem hoặc None nếu không tìm thấy
        """
    dlog.dlog_i(f"---GET cake by cake_names: {cake_names}")
    cake_dao = CakeDAO()
    return cake_dao.get_cakes_by_names(cake_names)
