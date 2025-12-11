from typing import List
from openai import OpenAI

from dconfig import config_object


class EmbeddingService:
    """Dịch vụ tạo embedding vector sử dụng OpenAI"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.client: OpenAI = OpenAI(api_key=api_key)

    def create_embedding(self, text: str) -> List[float]:
        """Tạo vector embedding từ văn bản"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Lỗi khi tạo embedding: {str(e)}")
