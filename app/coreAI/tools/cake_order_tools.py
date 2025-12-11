import json
from math import sqrt
from datetime import datetime
from typing import Optional, Dict, List

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

import dlog
from common_utils.constants import MID_TIER_DISTANCE_KM, MID_TIER_FEE, STORE_LOCATIONS, EXTRA_ITEM_PRICES, \
    FREE_DELIVERY_DISTANCE_KM, STORE_COORDINATES
from common_utils.datetime_utils import is_valid_receive_time_cake_normal, is_valid_receive_time_cake_special
from coreAI import embedding_service

from database.dao.milvus.cake_dao import CakeDAO
from dconfig import config_object, config_messages
from services.cake_service import get_cakes_by_names


@tool(
    name_or_callable="get_store_locations",
    description="Trả về danh sách địa chỉ và liên hệ của các cửa hàng bánh.")
def get_store_locations_tool() -> str:
    """
        Tool trả về danh sách các cửa hàng với địa chỉ và số điện thoại.

        Returns:
            str: JSON bao gồm key "stores" với danh sách địa chỉ.
        """
    dlog.dlog_i("--- get_store_locations_tool start ---")
    result = {"stores": STORE_LOCATIONS}
    dlog.dlog_i(f"--- get_store_locations_tool end: {len(STORE_LOCATIONS)} items ---")
    return json.dumps(result, ensure_ascii=False)


# 2. Schema và tool tính giá cuối cùng
class CalculatePriceArgs(BaseModel):
    cake_base_price: float = Field(..., description="Giá gốc của bánh (VND)")
    delivery_fee: Optional[float] = Field(0, description="Phí giao hàng (VND)")
    extra_items: Optional[Dict[str, int]] = Field(
        None,
        description="Số lượng vật dụng thêm, keys: extra_plate_set, extra_hat, topper"
    )


@tool(
    name_or_callable="calculate_final_price",
    description="Tính toán tổng giá trị đơn hàng.Bao gồm giá bánh cơ bản, phí giao hàng (nếu có), và chi phí cho các vật dụng mua thêm.",
    args_schema=CalculatePriceArgs
)
def calculate_final_price_tool(cake_base_price: float, delivery_fee: Optional[float],
                               extra_items: Optional[Dict[str, int]]) -> str:
    """
    Tính toán tổng giá đơn hàng, validate input đồ extra.
    Args:
        cake_base_price (float): Giá gốc của bánh (VND)
        delivery_fee (Optional[float]): Phí giao hàng (VND)
        extra_items (Optional[Dict[str, int]]): Số lượng vật dụng thêm, keys: extra_plate_set, extra_hat, topper
    Returns:
        str: JSON bao gồm breakdown và tổng giá.
    """
    dlog.dlog_i("--- calculate_final_price_tool start ---")

    # Validate extra_items keys
    invalid_keys = [k for k in extra_items if k not in EXTRA_ITEM_PRICES]
    if invalid_keys:
        return json.dumps({"error": f"Key invalid in extra_items: {invalid_keys}"}, ensure_ascii=False)

    # Tính tổng
    delivery_fee = delivery_fee if delivery_fee else 0
    total = cake_base_price + delivery_fee
    extras_breakdown = []
    extra_cost = 0
    for key, qty in extra_items.items():
        if qty < 0:
            continue
        cost = EXTRA_ITEM_PRICES[key] * qty
        extra_cost += cost
        extras_breakdown.append({"item": key, "quantity": qty, "cost": cost})
    total += extra_cost

    result = {
        "base": "cake_base_price",
        "delivery": delivery_fee,
        "extras": extras_breakdown,
        "total": total
    }
    dlog.dlog_i(f"--- calculate_final_price_tool end: total={total} ---")
    return json.dumps(result, ensure_ascii=False)


class DeliveryFeeArgs(BaseModel):
    address: str = Field(..., description="Địa chỉ giao hàng chi tiết, bao gồm tên đường, quận/huyện, thành phố.")


# Hàm helper lấy tọa độ từ ORS
def get_coordinates_from_address_ors(address: str) -> Optional[Dict[str, float]]:
    """
    Lấy tọa độ (longitude, latitude) từ địa chỉ sử dụng OpenRouteService.
    """
    ORS_API_KEY = config_object.ORS_API_KEY
    url = "https://api.openrouteservice.org/geocode/search"
    params = {"api_key": ORS_API_KEY, "text": address, "size": 1}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        if features:
            coords = features[0]["geometry"]["coordinates"]
            return {"longitude": coords[0], "latitude": coords[1]}
    except Exception as e:
        dlog.dlog_e(f"Error geocoding address: {e}")
    return None


@tool(
    name_or_callable="calculate_delivery_fee",
    description="Tính phí giao hàng dựa trên khoảng cách giữa cửa hàng và địa chỉ khách.",
    args_schema=DeliveryFeeArgs
)
def calculate_delivery_fee_ors_tool(address: str) -> str:
    """
    Tính phí giao hàng với chính sách:
      - dưới 5km miễn phí
      - 5-10km phí cố định
      - trên 10km báo sau

    Args:
        address (str): Địa chỉ giao hàng chi tiết, bao gồm tên đường, quận/huyện, tính phố.
    Returns:
        str: JSON {distance_km: float, fee: int} hoặc error.
    """
    dlog.dlog_i(f"--- calculate_delivery_fee_ors_tool start: address={address} ---")
    fee = MID_TIER_FEE
    try:
        dest = get_coordinates_from_address_ors(address)
        if not dest:
            return json.dumps({"error": "Không thể xác định tọa độ địa chỉ."}, ensure_ascii=False)
        start = STORE_COORDINATES

        dx = dest["longitude"] - start["longitude"]
        dy = dest["latitude"] - start["latitude"]
        distance_km = sqrt(dx * dx + dy * dy) * 111
        if distance_km <= FREE_DELIVERY_DISTANCE_KM:
            fee = 0
        elif distance_km <= MID_TIER_DISTANCE_KM:
            fee = MID_TIER_FEE
        else:
            return json.dumps({"distance_km": round(distance_km, 1), "fee": fee,
                               "error": config_messages.MESSAGE_HIGH_TIER_DISTANCE},
                              ensure_ascii=False)
        result = {"distance_km": round(distance_km, 1), "fee": fee}
    except Exception as e:
        dlog.dlog_e(f"Error calculating delivery fee: {e}")
        result = {"distance_km": "N/A", "fee": fee, "error": config_messages.MESSAGE_NOT_DISTANCE}
    dlog.dlog_i(f"--- calculate_delivery_fee_ors_tool end: {result} ---")
    return json.dumps(result, ensure_ascii=False)


class AvailabilityCheckArgs(BaseModel):
    cake_id: str = Field(..., description="Mã bánh kem đặt")
    cake_size: float = Field(..., description="Kích thước bánh (cm)")
    cake_price: float = Field(..., description="Giá đã đặt (VND)")
    receive_time: str = Field(
        ..., description="Thời gian nhận bánh (YYYY-MM-DD HH:MM)"
    )


@tool(
    name_or_callable="check_cake_availability",
    description="Kiểm tra thời gian nhận bánh của khách hàng có đủ để đầu bếp kịp làm không và tình trạng sẵn có của bánh (Cực kỳ cần thiết để tư vấn cho khách hàng).",
    args_schema=AvailabilityCheckArgs
)
def check_cake_availability_tool(cake_id: str, cake_size: float, cake_price: float, receive_time: str) -> str:
    """
    Kiểm tra thời gian nhận bánh của khách hàng có đủ để đầu bếp kịp làm không và tình trạng sẵn có của bánh (Cực kỳ cần thiết để tư vấn cho khách hàng).

    Args:
        cake_id (str): Mã bánh kem.
        cake_size (float): Kích thước bánh (cm).
        cake_price (float): Giá bánh (VND).
        receive_time (str): Thời gian nhận bánh (YYYY-MM-DD HH:MM).
    Returns:
        str: JSON {available: bool, reason?: str, min_ready_time?: str}.
    """
    min_ready_time = "N/A"
    dlog.dlog_i("--- check_cake_availability_tool start ---")
    available = False
    # TODO GET cake from API
    cakes_availability = {
        "01111.22": {"12.0": 190000, "16.0": 260000},
        "01111.23": {"12.0": 140000, "16.0": 200000},
        "01111.24": {"12.0": 160000, "16.0": 220000},
        "01111.25": {"18.0": 260000, "20.0": 280000}
    }

    if cake_id in cakes_availability.keys():
        cake = cakes_availability[cake_id]
        if str(cake_size) in cake.keys():
            available = True
            reason = config_messages.MESSAGE_FOUND_CAKE_AVAILABILITY.format(shop="cơ sở 1")
            return json.dumps({"available": available, "reason": reason, "min_ready_time": min_ready_time},
                              ensure_ascii=False)
        else:
            reason = config_messages.MESSAGE_FOUND_CAKE_NOT_SIZE.format(cake_name=cake_id,
                                                                        cake_size=cake_size)
    else:
        now = datetime.now()
        if not _is_special_cake(cake_id):
            available, min_ready_time = is_valid_receive_time_cake_normal(receive_time, now)
            if available:
                reason = config_messages.MESSAGE_FOUND_CAKE_AVAILABILITY_CHECK_TIME
            else:
                reason = config_messages.MESSAGE_NOT_FOUND_CAKE_AVAILABILITY
        else:
            available, min_ready_time = is_valid_receive_time_cake_special(receive_time, now)
            if available:
                reason = config_messages.MESSAGE_FOUND_CAKE_AVAILABILITY_CHECK_TIME
            else:
                reason = config_messages.MESSAGE_NOT_FOUND_CAKE_SPECIAL_AVAILABILITY
    if isinstance(min_ready_time, datetime):
        min_ready_time = min_ready_time.strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps({"available": available, "reason": reason, "min_ready_time": min_ready_time}, ensure_ascii=False)


def _is_special_cake(cake_id):
    if cake_id in ["01212.35", "11002.1", "01212.36", "01312.6", "11002.2", "01212.38", "01212.39", "01212.11",
                   "01212.15"]:
        return True
    special_cake_types = [
        "bánh entrement", "entrement",
        "bánh su kem", "su kem", "choux",
        "bánh kem sữa tươi đặc biệt", "sữa tươi đặc biệt",
        "bánh kem fondant", "fondant",
        "bánh rồng", "rồng", "dragon"
    ]
    cake_dao = CakeDAO()
    query_list = [f'description like "%{type}%"' for type in special_cake_types]
    query = " or ".join(query_list)
    query += ' and  source == "BonPas"'
    cakes_info = cake_dao.query_cakes_by_like(query=query)
    if cakes_info:
        cakes_name = [cake["name"] for cake in cakes_info]
        if cake_id in cakes_name:
            return True
    return False


class CakeAvailabilityQuery(BaseModel):
    type_of_cake: Optional[str] = Field(None, description="Loại bánh (gato, mousse, cheesecake,...)")
    flavor: Optional[str] = Field(None, description="Hương vị (socola, dâu,...)")
    number_of_people: Optional[int] = Field(None, description="Số người ăn")
    special_requests: Optional[str] = Field(None, description="Yêu cầu đặc biệt")
    color_cake: Optional[str] = Field(None, description="Màu chính của bánh")
    cake_shape: Optional[str] = Field(None, description="Hình dáng bánh (tròn, vuông,...)")
    cake_tiers: Optional[int] = Field(None, description="Số tầng bánh")
    cake_decoration: Optional[str] = Field(None, description="Trang trí bánh")
    intended_for: Optional[str] = Field(None, description="Dành tặng cho (người yêu, bố mẹ, bạn bè, ông bà...)")
    occasion: Optional[str] = Field(None, description="Dịp (sinh nhật, cưới, khai trương, mừng thọ...)")
    price_target: Optional[float] = Field(None, description="Giá mục tiêu (VND)")
    price_min: Optional[float] = Field(None, description="Giá tối thiểu (VND)")
    price_max: Optional[float] = Field(None, description="Giá tối đa (VND)")
    size_target: Optional[float] = Field(None, description="Kích thước mục tiêu (cm)")
    size_min: Optional[float] = Field(None, description="Kích thước tối thiểu (cm)")
    size_max: Optional[float] = Field(None, description="Kích thước tối đa (cm)")
    exclude_names: Optional[List[str]] = Field(None, description="Danh sách mã bánh loại trừ")


@tool(
    name_or_callable="get_cake_availability_tool",
    description="Tìm kiếm bánh có sẵn trong cửa hàng dựa trên bộ lọc chi tiết",
    args_schema=CakeAvailabilityQuery
)
def get_cake_availability_tool(type_of_cake: Optional[str],
                               flavor: Optional[str],
                               number_of_people: Optional[int],
                               special_requests: Optional[str],
                               color_cake: Optional[str],
                               cake_shape: Optional[str],
                               cake_tiers: Optional[int],
                               cake_decoration: Optional[str],
                               intended_for: Optional[str],
                               occasion: Optional[str],
                               price_min: Optional[float],
                               price_max: Optional[float],
                               size_min: Optional[float],
                               size_max: Optional[float],
                               price_target: Optional[float],
                               size_target: Optional[float],
                               exclude_names: Optional[List[str]],

                               ) -> str:
    """
    Trả về thông tin các loại bánh có sẵn, áp dụng bộ lọc và loại bỏ exclude_names.

    Args:
        type_of_cake (str): Loại bánh (gato, mousse, cheesecake,...).
        flavor (str): Hương vị (socola, dâu,...).
        number_of_people (int): Số người ăn.
        special_requests (str): Yêu cầu đặc biệt.
        color_cake (str): Màu chính của bánh.
        cake_shape (str): Hình dáng bánh (tròn, vuông,...).
        cake_tiers (int): Số tầng bánh.
        cake_decoration (str): Trang trí bánh.
        intended_for (str): Dành tặng cho (người yêu, bố mẹ, baise, ông bà...).
        occasion (str): Dịp (sinh nhật, cưới, khai trương, mừng thọ...).
        price_target (float): Giá mục tiêu (VND).
        price_min (float): Giá tối thiểu (VND).
        price_max (float): Giá tối đa (VND).
        size_target (float): Kích thước mục tiêu (cm).
        size_min (float): Kích thước tối thiểu (cm).
        size_max (float): Kích thước tối đa (cm).
        exclude_names (List[str]): Danh sách má bánh loại trừ.
    Returns:
        str: JSON {cakes: [...]}, mảng rỗng nếu không có.
    """
    dlog.dlog_i("--- get_cake_availability_tool start ---")
    args = CakeAvailabilityQuery(
        type_of_cake=type_of_cake,
        flavor=flavor,
        number_of_people=number_of_people,
        special_requests=special_requests,
        color_cake=color_cake,
        cake_shape=cake_shape,
        cake_tiers=cake_tiers,
        cake_decoration=cake_decoration,
        intended_for=intended_for,
        occasion=occasion,
        price_target=price_target,
        price_min=price_min,
        price_max=price_max,
        size_target=size_target,
        size_min=size_min,
        size_max=size_max,
        exclude_names=exclude_names,
    )
    params = args.model_dump(exclude_none=True)
    # Xử lý price_target → price_min/price_max nếu cần
    if "price_target" in params:
        pt = params.pop("price_target")
        delta = pt * 0.2
        params.setdefault("price_min", max(0, pt - delta))
        params.setdefault("price_max", pt + delta)
    # Xử lý size_target → size_min/size_max nếu cần
    if "size_target" in params:
        st = params.pop("size_target")
        delta = st * 0.2
        params.setdefault("size_min", max(0, st - delta))
        params.setdefault("size_max", st + delta)

    # Tạo query mô tả cho embedding nếu cần
    query_parts = []
    for key in ["type_of_cake", "flavor", "number_of_people", "special_requests",
                "color_cake", "cake_shape", "cake_tiers", "cake_decoration"]:
        if key in params:
            query_parts.append(f"{key}: {params[key]}")

    description_vector = embedding_service.create_embedding(" ".join(query_parts)) if query_parts else None

    # Loại trừ
    exclude = params.pop("exclude_names", [])
    # Gọi DAO tìm kiếm kết hợp vector và bộ lọc
    dao = CakeDAO()
    cakes = dao.search_cake_by_combined_vectors(
        image_vector=None,
        description_vector=description_vector,
        top_k=config_object.TOP_K_RECOMMENDATION_CAKE,
        exclude_names=exclude,
        price_min=params.get("price_min"),
        price_max=params.get("price_max"),
        size_min=params.get("size_min"),
        size_max=params.get("size_max")
    )
    if not cakes:
        return json.dumps({"cakes": []}, ensure_ascii=False)
    dlog.dlog_i(f"--- get_cake_availability_tool end: count={len(cakes)} ---")
    return json.dumps({"cakes": cakes}, ensure_ascii=False, indent=2)


class CheckCakeInfoArgs(BaseModel):
    cake_id: Optional[str] = Field(None, description="Mã bánh kem mã khách hàng đặt")
    cake_size: Optional[float] = Field(None, description="Kích thước bánh kem (cm) mà khách hàng đặt")
    cake_price: Optional[float] = Field(None, description="Giá bánh kem (VND). mà khách hàng đặt")


@tool('check_cake_order_info', description="Kiểm tra thông tin bánh kem cơ bản.",
      args_schema=CheckCakeInfoArgs)
def check_cake_order_info(cake_id: Optional[str] = None, cake_size: Optional[float] = None,
                          cake_price: Optional[float] = None, ):
    """
    Kiểm tra thông tin bánh kem cơ bản.

    Agrs:
        cake_id (str): Mã bánh kem mã khách hàng đặt.
        cake_size (float): Kích thước bánh kem (cm) mà khách hàng đặt.
        cake_price (float): Giá bánh kem (VND). mà khách hàng đặt.
    :Returns:
        str: JSON {available: bool, reason?: str, cake_info?: {code: str, image_url: str, description: str}}.
    """
    dlog.dlog_i("--- check_cake_order_info_tool start ---")
    available = True
    reason = "Thông tin bánh kem đã đầy đủ thông tin về mã bánh, size bánh, giá bánh"
    if cake_id is None:
        available = False
        reason = "Không thấy thông tin khách hàng chọn mã bánh"
    cake_info = {}
    if cake_id is not None and cake_size is None and cake_price is None:
        available = False
        cakes = get_cakes_by_names([cake_id])
        if cakes:
            cake = cakes[-1]
            cake_info = {
                "code": cake.get("name", cake.get("id")),
                "image_url": cake.get("image_url"),
                "description": cake.get("description", "N/A")
            }
        reason = "Không thấy thông tin khách hàng chọn size bánh và giá bánh"
    dlog.dlog_i("--- check_cake_order_info_tool end ---")
    return json.dumps({"available": available, "reason": reason, "cake_info": cake_info}, ensure_ascii=False)
