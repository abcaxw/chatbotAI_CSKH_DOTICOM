from dataclasses import dataclass, asdict
from typing import List, Optional, Union, Literal

from pydantic import Field, BaseModel


@dataclass
class BaseData:
    _id: str
    created_at: str = None
    updated_at: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Customer:
    _id: str
    platform: str = None
    platform_customer_id: str = None
    created_at: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Faq:
    title: str = None
    question: str = None
    answer: str = None
    source: str = None
    user: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class FaqData(Faq, BaseData):
    vector: list = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Thread:
    _id: str
    user_id: str
    platform: str = None
    created_at: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Message:
    _id: str
    thread_id: str = None
    user_id: str = None
    user_message: str = None
    bot_message: str = None
    bot_url: str = None
    bot_recommendation: str = None
    platform: str = None
    platform_message_id: str = None
    created_at: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class RecommendationQuestion:
    category: str
    question: str
    created_at: str = None
    updated_at: str = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ZaloAppChat:
    app_name: str
    app_id: str  # id của facebook hoặc zalo
    source: str  # vndirect , pti ...
    oa_secret_key: Optional[str]  # key xác thực OA
    app_secret_key: Optional[str]
    access_token: Optional[str]  # key xác thực khi qua API
    refresh_token: Optional[str]  # key lấy lại access_token (chỉ thấy ở zalo)
    created_at: str = None
    updated_at: str = None
    expires_in: float = 90000  # thời gian access_token được sử dụng trong 25h với zalo

    def to_dict(self):
        return asdict(self)


@dataclass
class PaginationData:
    page_number: int = Field(1, gt=0)
    page_size: int = Field(20, gt=0, lt=51)
    sort: Union[Literal['asc', 'desc']] = "desc"


@dataclass
class FaqPaginationData(PaginationData):
    question: str = None
    title: str = None


class DocumentPaginationData(PaginationData):
    title: str = None
    url: str = None
    category_id: int = None
    created_at: str = None
    creator: str = None


@dataclass
class Document:
    title: str
    category_id: int
    filename: str = None
    doc_type: str = None
    user_id: str = None
    content: str = None
    url: str = None


@dataclass
class QuestionDataData:
    question: str
    user_id: str
    platform: str


@dataclass
class ChunkRawData:
    document_id: int
    content: str


@dataclass
class Category:
    name: str
    status: str

@dataclass
class CakeData:
    name: str
    image_url: str
    description: str
    prices: list
    form: list
    source: str

    def to_dict(self):
        return asdict(self)
