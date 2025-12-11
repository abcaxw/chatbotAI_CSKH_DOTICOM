from pydantic import Field, BaseModel
from typing import TypedDict, List, Optional, Dict, Any

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    customer: Optional[str] = Field(default=None)
    platform: Optional[str] = Field(default=None)
    human_message: str = Field(default=None)
    ai_message: Optional[str] = Field(default=None)
    documents: Optional[List[str]] = Field(default_factory=list)
    messages: List[BaseMessage] = Field(default_factory=list)
    next_agent: Optional[str] = Field(default=None)
    current_agent: Optional[str] = Field(default=None)
    previous_agent: Optional[str] = Field(default=None)
    agent_status: Optional[str] = Field(default=None)
    thread_id: Optional[str] = Field(default=None)
    cake_information: Optional[str] = Field(default=None)
    # tool_messages: Optional[List[Any]] = Field(default_factory=list)
    presented_cake_names: List[str] = Field(default_factory=list)
    last_query_params: Optional[Dict[str, Any]] = Field(default=None)
    order_cakes_information: Optional[list[Dict[str, Any]]] = Field(default_factory=list)


class OrderCakeInformation(BaseModel):
    cake_id: Optional[str] = Field(default=None, description="Mã bánh kem (Không thể None)")
    cake_size: Optional[str] = Field(default=None, description="Size bánh kem (Không thể None)")
    cake_price: Optional[str] = Field(default=None, description="Giá bánh kem (Không thể None)")
    delivery_method: Optional[str] = Field(default=None,
                                           description="Hình thức nhận bánh kem 'nhận tại cửa hàng' hoặc 'giao tại nơi'")
    address: Optional[str] = Field(default=None,
                                   description="Địa chỉ cửa hàng, hoặc địa chỉ khách hàng (Không thể None, hãy đưa ra địa chỉ cửa hàng cho khách hàng chọn)")
    receive_time: Optional[str] = Field(default=None,
                                                description="Thời gian khách hàng nhận bánh kem(Không thể None) format theo dạng ISO (YYYY-MM-DD HH:MM)")
    customer_name: Optional[str] = Field(default=None, description="Tên khách hàng (Không thể None)")
    customer_phone: Optional[str] = Field(default=None, description="Số điện thoại khách hàng (Không thể None)")
    note: Optional[str] = Field(default=None,
                                description="Ghi chú từ khách hàng")
    cake_quantity: Optional[int] = Field(default=1, description="số lượng bánh kem")
    candle_number: Optional[int] = Field(default=None,
                                         description="nến số (Không thể None)")  # Check is number
    writing_on_cake: Optional[str] = Field(default=None,
                                           description="chữ viết trên bánh kem (Không thể None)")
    items: Optional[str] = Field(default=None,
                                 description="Vật dụng khác hàng mua thêm (mũ, pháo bông, bộ đĩa-bát...)")
    delivery_fee: Optional[int] = Field(default=None, description="Phí giao hàng (Không thể None)")
    price_summary: Optional[int] = Field(default=None, description="Tổng giá bánh kem, vật dụng khác, phí giao hàng (Không thể None)")

    def to_dict(self):
        return self.model_dump()

    def to_string(self):
        def format_line(label, value, key):
            return f"- `{key}` ({label}): {value if value else 'chưa hoàn thành'}"

        parts = [
            format_line("Mã bánh", self.cake_id, "cake_id"),
            format_line("Size", self.cake_size, "cake_size"),
            format_line("Giá", self.cake_price if self.cake_price is not None else "chưa hoàn thành", "cake_price"),
            format_line("Hình thức nhận hàng", self.delivery_method if self.delivery_method is not None else "chưa có",
                        "delivery_method"),
            format_line("Địa chỉ/Cửa hàng", self.address, "address"),
            format_line("Thời gian nhận", self.receive_time, "receive_time"),
            format_line("Tên KH", self.customer_name, "customer_name"),
            format_line("SĐT KH", self.customer_phone, "customer_phone"),
            format_line("Ghi chú", self.note, "note"),
            format_line("Chữ trên bánh", self.writing_on_cake, "writing_on_cake"),
            format_line("Vật dụng thêm", self.items, "items"),
            format_line("Số lượng bánh kem", self.cake_quantity if self.cake_quantity is not None else 1,
                        "cake_quantity"),
            format_line("Nến số", self.candle_number, "candle_number"),
        ]

        return "\n".join(parts)
