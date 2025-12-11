import json
import urllib.parse
import uuid

import requests
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import dlog
from object_models.agent_state_obj import OrderCakeInformation
from services.bill_service import insert_bill, update_bill, get_bills_by_customer_id


class SubmitOrderArgs(BaseModel):
    """
    Schema cho việc submit đơn hàng mới.
    """
    customer_id: int = Field(..., description="ID của khách hàng")
    items: List[OrderCakeInformation] = Field(..., description="Danh sách các mục bánh trong đơn hàng")
    final_price: float = Field(..., description="Tổng số tiền của hóa đơn (VND)")


class UpdateOrderArgs(BaseModel):
    """
    Schema cho việc cập nhật thông tin đơn hàng.
    """
    customer_id: int = Field(..., description="ID của khách hàng")
    bill_id: str = Field(..., description="Mã hóa đơn cần cập nhật")
    items: List[OrderCakeInformation] = Field(..., description="Danh sách các mục bánh đã chỉnh sửa")
    final_price: float = Field(..., description="Tổng số tiền mới của hóa đơn (VND)")


class GetBillHistoryArgs(BaseModel):
    """
    Schema cho việc lấy lịch sử hóa đơn của khách hàng.
    """
    customer_id: int = Field(..., description="ID của khách hàng")
    limit: int = Field(1, description="Số lượng hóa đơn gần nhất cần lấy")


def build_order_url(json_list, order_id="dh765"):
    """
    Builds URLs for order API from JSON data.

    Args:
        json_list: List of JSON strings containing order data
        order_id: Order ID to use (default: "dh765")

    Returns:
        List of URLs for the API calls
    """
    base_url = "https://doticom.vn/api/aidatbanhkem.php?"
    urls = []

    for json_str in json_list:
        # Parse JSON string to dictionary
        order = json.loads(json_str) if isinstance(json_str, str) else json_str

        # Xử lý các trường có thể thiếu hoặc null
        params = {
            "orderId": order_id,
            "cakename": order.get("cake_id", ""),
            "name": order.get("customer_name", ""),
            "phone": order.get("customer_phone", ""),
            "price": order.get("cake_price", ""),
            "cakeMessage": order.get("writing_on_cake", ""),
            "numberCandles": order.get("candle_number", "") or "NULL",
            "address": order.get("address", "").replace(" ", "_"),
            "cakeId": order.get("cake_id", ""),
            "totalPrice": order.get("final_price_summary", order.get("cake_price", "")),
            "deliveryTime": order.get("receive_time", ""),
            "notes": order.get("note", "") or "",
            "accessories": order.get("items", "") or "",
            "deliveryMethod": order.get("delivery_method", ""),
            "cakeSize": order.get("cake_size", "") or "",
            "deliveryFee": order.get("delivery_fee", "") or "0"
        }

        # Encode parameters and append to base URL
        query_string = urllib.parse.urlencode(params, doseq=True)
        full_url = base_url + query_string
        urls.append(full_url)

    return urls


def generate_chatbot_management_url(order_id):
    """
    Tạo URL quản lý đơn hàng cho khách hàng thông qua chatbot.

    Args:
        order_id: Mã đơn hàng

    Returns:
        str: URL quản lý đơn hàng
    """
    return f"https://doticom.vn/chatbot.php?id={order_id}"


@tool(
    name_or_callable="submit_order_api",
    description=(
            "Giúp khách hàng **tạo đơn hàng** đặt bánh mới một cách nhanh chóng và hiệu quả."
            "Trả về bill_id của hóa đơn vừa tạo."
    ),
    args_schema=SubmitOrderArgs
)
def submit_order_api_tool(customer_id: int,
                          items: List[OrderCakeInformation], final_price: float) -> str:
    """
    Xử lý tạo đơn hàng và lưu vào hệ thống.

    Args:
        customer_id (int): ID của khách hàng.
        items (List[OrderCakeInformation]): Danh sách các mục bánh trong đơn hàng.
        final_price (float): Tổng số tiền của hóa đơn (VND).

    Returns:
        str: bill_id vừa được sinh ra và các URL xác nhận đơn hàng.
    """
    dlog.dlog_i("--- submit_order_api_tool start ---")
    bill_id = f"{customer_id}-{int(final_price)}-{uuid.uuid4()}"

    # Lưu vào database
    insert_bill(
        [item.model_dump() for item in items],
        final_price,
        customer_id,
        bill_id
    )

    # Tạo các URL cho API
    json_data = []
    for item in items:
        item_dict = item.model_dump() if hasattr(item, 'dict') else item.to_dict()
        # Thêm giá cuối cùng vào item_dict
        item_dict["final_price_summary"] = final_price
        json_data.append(item_dict)

    # Xây dựng URL với bill_id làm order_id
    urls = build_order_url(json_data, order_id=bill_id)

    # Tạo URL quản lý đơn hàng cho khách hàng
    chatbot_management_url = generate_chatbot_management_url(bill_id)

    # Log URLs được tạo
    for url in urls:
        dlog.dlog_i(f"Order URL: {url}")

    dlog.dlog_i(f"Chatbot Management URL: {chatbot_management_url}")

    # Thực hiện gửi yêu cầu đến cửa hàng để xác nhận đơn hàng
    confirmation_results = []
    try:

        for i, url in enumerate(urls):
            dlog.dlog_i(f"Đang gửi yêu cầu xác nhận đơn hàng #{i + 1} tới cửa hàng...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                confirmation_results.append(f"Đã xác nhận đơn hàng #{i + 1} thành công!")
                dlog.dlog_i(f"Xác nhận đơn hàng #{i + 1} thành công: {response.text[:100]}...")
            else:
                confirmation_results.append(f"Lỗi khi xác nhận đơn hàng #{i + 1}: {response.status_code}")
                dlog.dlog_i(f"Lỗi khi xác nhận đơn hàng #{i + 1}: {response.status_code}")
    except Exception as e:
        dlog.dlog_i(f"Có lỗi xảy ra khi gửi yêu cầu xác nhận: {str(e)}")
        confirmation_results.append(f"Có lỗi xảy ra khi gửi yêu cầu xác nhận: {str(e)}")

    result = {
        "bill_id": bill_id,
        "confirmation_results": confirmation_results,
        "confirmation_urls": urls,
        "chatbot_management_url": chatbot_management_url,
        "management_message": f"Bạn có thể theo dõi và quản lý đơn hàng của mình tại: {chatbot_management_url}"
    }

    dlog.dlog_i(f"--- submit_order_api_tool end: bill_id={bill_id} ---")
    return json.dumps(result, ensure_ascii=False)


@tool(
    name_or_callable="update_order_api",
    description="""Cập nhật đơn hàng đã tồn tại của khách hàng.\nTrả về bill_id nếu thành công.""",
    args_schema=UpdateOrderArgs
)
def update_order_tool(customer_id: int,
                      bill_id: str,
                      items: List[OrderCakeInformation],
                      final_price: float) -> str:
    """
    Xử lý cập nhật thông tin đơn hàng.

    Args:
        customer_id (int): ID của khách hàng.
        bill_id (str): Mã hóa đơn cần cập nhật.
        items (List[OrderCakeInformation]): Danh sách các mục bánh trong đơn hàng.
        final_price (float): Tổng số tiền mới của hóa đơn (VND).

    Returns:
        str: bill_id đã được cập nhật và các URL xác nhận đơn hàng.
    """
    dlog.dlog_i("--- update_order_tool start ---")
    update_bill(
        [item.to_dict() for item in items],
        final_price,
        customer_id,
        bill_id
    )

    # Tạo các URL cho API khi cập nhật đơn hàng
    json_data = []
    for item in items:
        item_dict = item.model_dump() if hasattr(item, 'dict') else item.to_dict()
        # Thêm giá cuối cùng vào item_dict
        item_dict["final_price_summary"] = final_price
        json_data.append(item_dict)

    # Xây dựng URL với bill_id làm order_id
    urls = build_order_url(json_data, order_id=bill_id)

    # Tạo URL quản lý đơn hàng cho khách hàng
    chatbot_management_url = generate_chatbot_management_url(bill_id)

    # Log URLs được tạo
    for url in urls:
        dlog.dlog_i(f"Updated Order URL: {url}")

    dlog.dlog_i(f"Chatbot Management URL: {chatbot_management_url}")

    # Thực hiện gửi yêu cầu đến cửa hàng để xác nhận đơn hàng đã cập nhật
    confirmation_results = []
    try:
        import requests
        for i, url in enumerate(urls):
            dlog.dlog_i(f"Đang gửi yêu cầu xác nhận đơn hàng đã cập nhật #{i + 1} tới cửa hàng...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                confirmation_results.append(f"Đã xác nhận cập nhật đơn hàng #{i + 1} thành công!")
                dlog.dlog_i(f"Xác nhận cập nhật đơn hàng #{i + 1} thành công: {response.text[:100]}...")
            else:
                confirmation_results.append(f"Lỗi khi xác nhận cập nhật đơn hàng #{i + 1}: {response.status_code}")
                dlog.dlog_i(f"Lỗi khi xác nhận cập nhật đơn hàng #{i + 1}: {response.status_code}")
    except Exception as e:
        dlog.dlog_i(f"Có lỗi xảy ra khi gửi yêu cầu xác nhận cập nhật: {str(e)}")
        confirmation_results.append(f"Có lỗi xảy ra khi gửi yêu cầu xác nhận cập nhật: {str(e)}")

    result = {
        "bill_id": bill_id,
        "confirmation_results": confirmation_results,
        "confirmation_urls": urls,
        "chatbot_management_url": chatbot_management_url,
        "management_message": f"Bạn có thể theo dõi và quản lý đơn hàng của mình tại: {chatbot_management_url}"
    }

    dlog.dlog_i(f"--- update_order_tool end: bill_id={bill_id} ---")
    return json.dumps(result, ensure_ascii=False)


@tool(
    name_or_callable="get_customer_bill_history",
    description=(
            "Lấy lịch sử hóa đơn đã đặt của khách hàng. "
            "Trả về danh sách hóa đơn dưới dạng JSON."
    ),
    args_schema=GetBillHistoryArgs
)
def get_customer_bill_history_tool(customer_id: int, limit: Optional[int] = 1) -> str:
    """
    Xử lý truy vấn lịch sử đơn hàng của khách hàng.

    Args:
        customer_id: int: ID của khách hàng.
        limit: int: Số lượng hóa đơn gần nhất cần lấy.
    Returns:
        str: JSON list các hoá đơn (id, thông tin) hoặc error message.
    """
    dlog.dlog_i("--- get_customer_bill_history_tool start ---")
    bills = get_bills_by_customer_id(customer_id, limit)

    # Nếu có bill, thêm URL quản lý cho mỗi hóa đơn
    if isinstance(bills, list):
        for bill in bills:
            bill_id = bill.get("bill_id")
            if bill_id:
                bill["chatbot_management_url"] = generate_chatbot_management_url(bill_id)

    dlog.dlog_i(
        f"--- get_customer_bill_history_tool end: found {len(bills) if isinstance(bills, list) else 0} bills ---")
    return bills if isinstance(bills, str) else json.dumps(bills, ensure_ascii=False)