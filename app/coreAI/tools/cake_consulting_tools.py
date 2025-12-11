import json
import re
from datetime import datetime
from typing import Optional, List, Dict

import numpy as np
from langchain_core.tools import tool
from pydantic import Field, BaseModel

import dlog
from common_utils.constants import OCCASIONS, COLORS, DECORATIONS, FLAVORS, TYPE_OF_CAKES, INDENTED_FORS
from common_utils.datetime_utils import is_valid_receive_time_cake_special, \
    is_valid_receive_time_cake_normal
from coreAI import embedding_image_model, embedding_service, cake_detector
from database.dao.milvus.cake_dao import CakeDAO
from dconfig import config_object, config_messages
from services.cake_service import get_cakes_by_names


class CakeQuery(BaseModel):
    """
    Schema cho truy vấn bánh kem.
    """
    type_of_cake: Optional[str] = Field(None,
                                        description="Loại bánh (gato, tiramisu, mousse, cheesecake, cupcake, entrement ...)")
    flavor: Optional[str] = Field(None, description="Hương vị (socola, dâu, chanh leo, việt quất, xoài ...)")
    number_of_people: Optional[int] = Field(None, description="Số lượng người dùng bánh")
    image_link: Optional[str] = Field(None, description="URL ảnh mẫu tham khảo (luôn lấy link ảnh mới nhất)")
    special_requests: Optional[str] = Field(None, description="Yêu cầu đặc biệt thêm (nội dung, ghi chữ...)")
    cake_information_old: Optional[str] = Field(None, description="Ghi chú/thông tin bánh cũ do khách đã cung cấp")
    color_cake: Optional[str] = Field(None,
                                      description="Màu sắc chủ đạo của bánh (hồng, tím, xanh lá, trắng, vàng, nâu, đỏ, đen, xanh dương, cam...)")
    cake_shape: Optional[str] = Field(None, description="Hình dáng bánh (tròn, vuông, trái tim...)")
    cake_tiers: Optional[int] = Field(None, description="Số tầng của bánh")
    cake_decoration: Optional[str] = Field(None,
                                           description="Phong cách hoặc vật trang trí (hoa, quả dâu tây, chai rượu, mô hình, siêu nhân, khủng long, công chúa, trái cây, chocolate, hạt trái cây, nụ hồng...)")
    intended_for: Optional[str] = Field(None,
                                        description="Dành tặng cho ai (vợ, chồng, người yêu, bố, mẹ, bạn bè, ông, bà, con trai, con gái, bé trai, bé gái...)")
    occasion: Optional[str] = Field(None, description="Dịp (tiệc ăn mừng, sinh nhật, cưới, khai trương, mừng thọ...)")
    best_seller: Optional[str] = Field(None, description="Bánh bán chạy nhất")
    recommend_cake: Optional[str] = Field("bánh thường", description="Recommended cake")
    price_target: Optional[float] = Field(None, description="Mức giá mục tiêu (VND)")
    price_min: Optional[float] = Field(None, description="Giá tối thiểu (VND), giá rẻ nhất (VND), giá thấp nhất (VND)")
    price_max: Optional[float] = Field(None, description="Giá tối đa (VND), giá mắc nhất(VND), giá cao nhất (VND)")
    size_target: Optional[float] = Field(None, description="Kích thước mục tiêu (cm)")
    size_min: Optional[float] = Field(None, description="Kích thước tối thiểu (cm)")
    size_max: Optional[float] = Field(None, description="Kích thước tối đa (cm)")
    exclude_names: Optional[List[str]] = Field(None, description="Danh sách mã/tên bánh cần loại bỏ")


@tool(
    name_or_callable="retriever_cake_information",
    description="""
    Nhận vào tham số tìm kiếm bánh kem dưới dạng JSON theo schema CakeQuery(type_of_cake, flavor, image_link mới nhất, color_cake...) , trả về danh sách bánh phù hợp (đã loại trừ exclude_names) dưới dạng JSON. Nếu không tìm thấy bánh phù hợp với tiêu chí, sẽ tự động trả về bánh bán chạy nhất.
    """,
    args_schema=CakeQuery
)
def retriever_cake_information_tool(type_of_cake: Optional[str] = None,
                                    flavor: Optional[str] = None,
                                    number_of_people: Optional[int] = None,
                                    image_link: Optional[str] = None,
                                    special_requests: Optional[str] = None,
                                    cake_information_old: Optional[str] = None,
                                    color_cake: Optional[str] = None,
                                    cake_shape: Optional[str] = None,
                                    cake_tiers: Optional[int] = None,
                                    cake_decoration: Optional[str] = None,
                                    intended_for: Optional[str] = None,
                                    occasion: Optional[str] = None,
                                    best_seller: Optional[str] = None,
                                    recommend_cake: Optional[str] = "bánh thường",
                                    price_target: Optional[float] = None,
                                    price_min: Optional[float] = None,
                                    price_max: Optional[float] = None,
                                    size_target: Optional[float] = None,
                                    size_min: Optional[float] = None,
                                    size_max: Optional[float] = None,
                                    exclude_names: Optional[List[str]] = None):
    """
    Retrieve cake-related information based on provided parameters (type_of_cake, flavor, number_of_people, image_link mới nhất, best_seller, bán chạy ...).
    Nếu không tìm thấy kết quả phù hợp, sẽ tự động trả về bánh bán chạy nhất.
    Args:
        type_of_cake: Loại bánh (gato, tiramisu, mousse, cheesecake, cupcake, ...)
        flavor: Hương vị (socola, dâu, chanh leo, việt quất, ...)
        number_of_people: Số lượng người dùng bánh
        image_link: URL ảnh mẫu tham khảo (luôn lấy link ảnh mới nhất)
        special_requests: Yêu cầu đặc biệt thêm (nội dung, ghi chữ...)
        cake_information_old: Ghi chú/thông tin bánh cũ do khách hàng cung cấp
        color_cake: Màu sắc chủ đạo bánh (hồng, tím, xanh lá, trắng, vàng, nâu, đỏ, đen, xanh dương, cam...)
        cake_shape: Hình dáng bánh (tròn, vuông, trái tim...)
        cake_tiers: Số tầng bánh
        cake_decoration: Phong cách hoặc vật trang trí (hoa, quả dâu tây, chai rượu, mô hình, siêu nhân...)
        intended_for: Dành tặng cho (người yêu, bố mẹ, bạn bè, ông bà...)
        occasion: Dịp (sinh nhật, cưới, khai trương, mừng thọ...)
        best_seller: Bánh bánh chạy nhất (best seller, hot deal, bán chạy nhất ...)
        recommend_cake: Chọn một trong 3 loại bánh: bánh thường, bánh có sẵn, bánh thường + bánh đặc biệt (default: bánh thường)
        price_target: Mức giá mục tiêu (VND)
        price_min: Giá tối thiểu (VND)
        price_max: Giá tối đa (VND)
        size_target: Kích thước mục tiêu (cm)
        size_min: Kích thước tối thiểu (cm)
        size_max: Kích thước tối đa (cm)
        exclude_names: Danh sách mã/tên bánh cần loại bỏ

    Returns:
        str: JSON-formatted list of cakes, mỗi phần tử có:
            - id/code: mã định danh
            - description: mô tả chi tiết (hình dạng kích thước, giá, hương vị ...)
            - image_url: link ảnh
            - is_fallback: true nếu là kết quả fallback (bánh bán chạy nhất)
        Nếu không tìm thấy, trả về JSON: {"error": "message not found"}.
    """
    args = CakeQuery(
        type_of_cake=type_of_cake,
        flavor=flavor,
        number_of_people=number_of_people,
        image_link=image_link,
        special_requests=special_requests,
        cake_information_old=cake_information_old,
        color_cake=color_cake,
        cake_shape=cake_shape,
        cake_tiers=cake_tiers,
        cake_decoration=cake_decoration,
        intended_for=intended_for,
        occasion=occasion,
        best_seller=best_seller,
        recommend_cake=recommend_cake,
        price_target=price_target,
        price_min=price_min,
        price_max=price_max,
        size_target=size_target,
        size_min=size_min,
        size_max=size_max,
        exclude_names=exclude_names,
    )
    dlog.dlog_i(f"---retriever_cake_information_tool---")

    # Unpack args
    params = args.model_dump(exclude_none=True)
    # Ghi log các tham số đã được xử lý
    exclude_names = params.pop("exclude_names", None)

    recommend_cake = params.pop("recommend_cake", 'bánh thường').lower()
    has_search_criteria = bool(params)
    cakes = []
    image_vector_list = []
    if has_search_criteria:

        dlog.dlog_i(
            f"Processed parameters: color={params.get('color_cake')}, decoration={params.get('cake_decoration')}, flavor={params.get('flavor')}, type={params.get('type_of_cake')}, intended={params.get('intended_for')}, occasion = {params.get('occasion')}")
        # Xử lý tự động price_target → price_min/max
        price_target = params.pop("price_target", None)
        if price_target is not None:
            delta = price_target * 0.2
            params.setdefault("price_min", max(0, price_target - delta))
            params.setdefault("price_max", price_target + delta)

        # Xử lý size_target → size_min/max
        size_target = params.pop("size_target", None)
        if size_target is not None:
            delta = size_target * 0.2
            params.setdefault("size_min", max(0, size_target - delta))
            params.setdefault("size_max", size_target + delta)

        keys = ["color_cake", "cake_decoration", "flavor", "type_of_cake", "intended_for", "occasion"]
        filter_keys = []
        list_keywords = [COLORS, DECORATIONS, FLAVORS, TYPE_OF_CAKES, INDENTED_FORS, OCCASIONS]
        # Xử lý đặc biệt cho tham số color_cake, cake_decoration, flavor và type_of_cake
        for key, keywords in zip(keys, list_keywords):
            if key in params and params.get(key):
                filter_keys.append(params.get(key))
                description = find_description_by_keyword(params.get(key, ""), keywords)
                params[key] = description

        # Embedding (nếu có)
        img_list = None
        if params.get("image_link"):
            try:
                img_list = cake_detector.crop_from_image(params.pop("image_link"))
            except Exception as e:
                dlog.dlog_i(f"Error processing image: {e}")

        if img_list:
            for img in img_list:
                try:
                    image_vector = embedding_image_model.get_embedding(img)[0]
                    image_vector_list.append(image_vector)
                except Exception as e:
                    dlog.dlog_i(f"Error getting image embedding: {e}")

        # Tạo embedding từ mô tả với trọng số cao hơn cho tất cả các trường
        description_parts = []
        if params.pop("best_seller", None):
            description_parts.append(f"best seller")
        # Tạo description cho embedding
        for k, v in params.items():
            if v is not None and str(v).strip():
                description_parts.append(f"{k}: {v}")

        description = "\n".join(description_parts)
        description_vector = embedding_service.create_embedding(description) if description else None

        # Tăng top_k để đảm bảo đủ kết quả sau khi lọc
        top_k = config_object.TOP_K_RECOMMENDATION_CAKE * 2 if len(image_vector_list) == 0 else 3

        # Gọi DAO
        cake_dao = CakeDAO()

        if len(image_vector_list) == 0:
            cakes = cake_dao.search_cake_by_combined_vectors(
                description_vector=description_vector,
                recommend_cake=recommend_cake,
                top_k=top_k,
                exclude_names=exclude_names,
                price_min=params.get("price_min"),
                price_max=params.get("price_max"),
                size_min=params.get("size_min"),
                size_max=params.get("size_max"),
            )
        else:
            top_k = max(config_object.TOP_K_RECOMMENDATION_CAKE // len(image_vector_list), top_k)
            for image_vector in image_vector_list:
                cakes_data = cake_dao.search_cake_by_combined_vectors(
                    image_vector=image_vector,
                    description_vector=description_vector,
                    exclude_names=exclude_names,
                    recommend_cake=recommend_cake,
                    top_k=top_k,
                    price_min=params.get("price_min"),
                    price_max=params.get("price_max"),
                    size_min=params.get("size_min"),
                    size_max=params.get("size_max"),
                )
                seen = set(frozenset(d.items()) for d in cakes)
                for item in cakes_data:
                    item_key = frozenset(item.items())
                    if item_key not in seen:
                        cakes.append(item)
                        seen.add(item_key)

        # Giới hạn kết quả trả về
        if len(cakes) > config_object.TOP_K_RECOMMENDATION_CAKE:
            cakes = cakes[:config_object.TOP_K_RECOMMENDATION_CAKE]

    if len(cakes) == 0 or not cakes:
        dlog.dlog_i("Không có tiêu chí tìm kiếm, trả về bánh bán chạy nhất")
        has_search_criteria = False
        cakes = best_seller_cake(exclude_names)
        if not cakes:
            return json.dumps({"error": config_messages.MESSAGE_NOT_FOUND_CAKE}, ensure_ascii=False)
    dlog.dlog_i(f"Found {len(cakes)} cakes")
    # Chuẩn hoá kết quả
    results = []
    for c in cakes:
        cake_info = {
            "cake_id": c.get("name"),
            "image_url": c.get("image_url"),
            "description": c.get("description")
        }
        if not has_search_criteria:
            cake_info["is_fallback"] = True
            cake_info["fallback_reason"] = "Không có tiêu chí tìm kiếm, hiển thị bánh bán chạy nhất"
        results.append(cake_info)

    return json.dumps(results, ensure_ascii=False, indent=2)


def find_description_by_keyword(keyword: str, list_keywords: list) -> str:
    keywork_normal = keyword.lower().strip()

    results = []
    for keywords in list_keywords:
        if any(variant in keywork_normal for variant in keywords):
            results = keywords
            break

    if results:
        return ", ".join(results)
    else:
        return keyword


@tool('get_cake_information')
def get_cake_information_tool(cake_codes: list[str]):
    """
    Fetch basic information for one or more cake codes from the database.
    Args:
        cake_codes (List[str]): A list of cake identifier codes.

    Returns:
        str: A JSON-formatted string containing, for each cake:
            - code: the cake’s identifier code
            - image_url: the URL of the cake’s image
        If no codes are found, returns an error message.
    """
    dlog.dlog_i(f"get_cake_information {cake_codes}")
    cakes = get_cakes_by_names(cake_codes)
    if not cakes:
        return json.dumps({"error": config_messages.MESSAGE_NOT_FOUND_CAKE}, ensure_ascii=False)

    # Chỉ lấy code và image_url
    results = []
    for cake in cakes:
        results.append({
            "code": cake.get("name"),
            "image_url": cake.get("image_url"),
            "description": cake.get("description", "N/A")
        })

    return json.dumps(results, ensure_ascii=False, indent=2)


@tool('get_best_seller_cakes')
def get_best_seller_cakes(exclude_names: Optional[List[str]] = None,
                          top_k: int = config_object.TOP_K_RECOMMENDATION_CAKE) -> List[dict]:
    """
    Retrieve a list of best-selling cakes when no suitable results are found.

    Args:
        exclude_names: List of cake names to exclude
        top_k: Number of cakes to retrieve

    Returns:
        List[dict]: A list of the top-selling cakes
    """

    dlog.dlog_i("Không tìm thấy bánh phù hợp với tiêu chí, đang lấy bánh bán chạy nhất...")

    best_seller_cakes = best_seller_cake(exclude_names=exclude_names, top_k=top_k)
    return best_seller_cakes


def best_seller_cake(exclude_names: Optional[List[str]] = None, top_k: int = config_object.TOP_K_RECOMMENDATION_CAKE):
    best_seller_description = "best seller bán chạy nhất hot deal phổ biến"
    description_vector = embedding_service.create_embedding(best_seller_description)
    cake_dao: CakeDAO = CakeDAO()
    # Tìm kiếm bánh bán chạy với top_k cao hơn để có nhiều lựa chọn
    best_seller_cakes = cake_dao.search_cake_by_combined_vectors(
        description_vector=description_vector,
        top_k=top_k,  # Lấy nhiều hơn để có thể filter
        exclude_names=exclude_names
    )
    return best_seller_cakes


@tool("suggest_cake_type")
def suggest_cake_type(order_dt: str) -> Dict[str, object]:
    """
    Suggest which type of cake to recommend to a customer based on the current time
    and the desired pickup time, returning detailed availability and recommendation.

    Rules:
    - If the pickup time is < 3 hours from now → recommend "bánh có sẵn"
    - If the pickup time is between 3 and 12 hours → recommend "bánh thường"
    - If the pickup time is more than 12 hours → recommend "bánh thường + bánh đặc biệt"

    Args:
        order_dt (str): Desired pickup time in "YYYY-MM-DD HH:MM" format.

    Returns:
        Dict[str, object]: A dictionary containing:
            - available_standard (bool): Whether a standard cake can be ready < 3 hours.
            - available_special (bool): Whether a special cake can be ready 3 ->12 hours.
            - recommendation (str): One of "bánh có sẵn", "bánh thường", or "bánh thường + bánh đặc biệt"
    """
    dlog.dlog_i(f"Suggest cake type: {order_dt}")
    # Parse current and order times
    now_time = datetime.now()

    # Check availability
    available_standard, min_ready_time = is_valid_receive_time_cake_normal(order_dt, now_time)
    available_special, _ = is_valid_receive_time_cake_special(order_dt, now_time)

    # Determine recommendation
    if available_standard:
        recommendation = "bánh thường"
        if available_special:
            recommendation = "bánh thường + bánh đặc biệt"
    else:
        recommendation = "bánh có sẵn"

    return {
        "available_standard": available_standard,
        "available_special": available_special,
        "recommendation": recommendation
    }


@tool("get_available_cakes")
def get_available_cakes():
    """
    Function to retrieve the list of cakes currently available in the store.

    Returns:
        List[str]: A list of URLs for cakes available in the store.
    """
    dlog.dlog_i("Lấy danh sách bánh có sẵn")
    cakes = {
        "01111.22": {"12.0": 190000, "16.0": 260000},
        "01111.23": {"12.0": 140000, "16.0": 200000},
        "01111.24": {"12.0": 160000, "16.0": 220000},
        "01111.25": {"18.0": 260000, "20.0": 280000}
    }
    link_cake = [f"https://doticom.vn/lichhop/DataFile/bonpas/ImgBig/{cake_id}.jpg" for cake_id in list(cakes.keys())]
    return link_cake


@tool("get_available_cake_info")
def get_available_cake_info(cake_id: str):
    """
    Function to retrieve price and size information of cakes available (recommendation == 'bánh có sẵn') in the store by cake_id.

    Args:
        cake_id (str): the identifier of the cake

    Returns:
        dict: {
            "description": description,
            "cake_available": {
                size: price
            }
        }
    }
    """
    dlog.dlog_i(f"---GET cake info {cake_id}")
    cakes = {
        "01111.22": {"12.0": 190000, "16.0": 260000},
        "01111.23": {"12.0": 140000, "16.0": 200000},
        "01111.24": {"12.0": 160000, "16.0": 220000},
        "01111.25": {"18.0": 260000, "20.0": 280000}
    }
    cake_dao = CakeDAO()
    cakes_info = cake_dao.get_cakes_by_names([cake_id])
    cake_info = {}
    if cakes_info:
        cake_info = cakes_info[0]
    description = cake_info.get("description")
    result = {"description": description}
    if cake_id in cakes:
        result["cake_available"] = cakes[cake_id]
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool("check_order_cake_by_image")
def check_order_cake_by_image(image_url: str, exclude_names: Optional[List[str]] = None, ) -> Dict[str, object]:
    """
    Function to check order cake by image.

    Args:
        image_url (str): the url of image
        exclude_names: List of cake codes/names to exclude
    Returns:
        dict: {
            "available": available,
            "description": description}
    """
    try:
        dlog.dlog_i(f"check_order_cake_by_image {image_url}")
        cake_similar = {}
        if image_url.startswith("https://doticom.vn/lichhop/DataFile/bonpas/ImgBig/"):
            code = re.findall(r'/ImgBig/([A-Za-z0-9.-]+)\.jpg', image_url)[0]
            cake_info = get_cakes_by_names([code])
            cake_similar = {
                "accuracy": 1,
                "code": code,
                "image_url": image_url,
                "description": cake_info[0].get("description")
            }
        else:
            image_vector = embedding_image_model.get_embedding(image_url)[0]

            if exclude_names is None:
                exclude_names = []

            for code in exclude_names:
                img_url = f"https://doticom.vn/lichhop/DataFile/bonpas/ImgBig/{code}.jpg"
                exclude_image_vector = embedding_image_model.get_embedding(img_url)[0]
                cos_sim = np.dot(image_vector, exclude_image_vector) / (
                        np.linalg.norm(image_vector) * np.linalg.norm(exclude_image_vector))
                if cos_sim > 0.8:
                    if cake_similar.get("accuracy", 0) > cos_sim:
                        cake_info = get_cakes_by_names([code])
                        cake_similar = {
                            "accuracy": cos_sim,
                            "code": code,
                            "image_url": img_url,
                            "description": cake_info[0].get("description")
                        }

        if cake_similar:
            result = {"available": True,
                      "description": f"Khách hàng muốn đặt bánh Mã bánh {cake_similar['code']}, url: {cake_similar['image_url']}, {cake_similar['description']}"}
        else:
            result = {"available": False,
                      "description": f"AI chưa tư vấn cho khách, khách muốn tìm kiếm bánh giống bánh url: {image_url}"}
        dlog.dlog_i(f"check_order_cake_by_image result: {result}")
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        dlog.dlog_i(f"Error in check_order_cake_by_image: {e}")
        return json.dumps({"error": "Có lỗi xảy ra khi kiểm tra bánh theo ảnh"}, ensure_ascii=False)
