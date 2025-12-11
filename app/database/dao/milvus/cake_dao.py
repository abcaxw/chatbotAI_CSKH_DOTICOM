import traceback
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from pymilvus import AnnSearchRequest, RRFRanker, DataType

import dlog
from common_utils.string_utils import extract_sizes

from database.dao.milvus.base_dao import BaseDAO
from database import milvus_service


class CakeDAO(BaseDAO):
    COLLECTION_NAME = "cake"

    def __init__(self):
        super().__init__()
        self.client = self.get_client()

    def find_image_by_name(self, cake_name):
        filter = f"name == '{cake_name}'"
        res = self.client.query(
            collection_name=self.COLLECTION_NAME,
            filter=filter,
            output_fields=["id"]
        )
        return len(res)

    def search_cake_by_description(self, cakes_name=list,
                                   description_vector=None,
                                   exclude_names: Optional[List[str]] = None,
                                   source="BonPas", top_k=3,
                                   price_min: Optional[float] = None,
                                   price_max: Optional[float] = None,
                                   size_min: Optional[float] = None,
                                   size_max: Optional[float] = None):
        filter_conditions = []
        # Thêm điều kiện exclude_names
        if exclude_names:
            filter_conditions.append(f"name NOT IN {exclude_names}")
        if cakes_name:
            filter_conditions.append(f"name IN {cakes_name}")
        # Thêm điều kiện source
        filter_conditions.append(f"source == '{source}'")

        # Thêm điều kiện về price
        if price_min is not None:
            price_min = int(price_min)
            filter_conditions.append(f"price_min >= {price_min}")
        if price_max is not None:
            price_max = int(price_max)
            filter_conditions.append(f"price_max <= {price_max}")

        # Thêm điều kiện về size (mảng)
        if size_min is not None:
            size_min = int(size_min)
            filter_conditions.append(f"size_min >= {size_min}")
        if size_max is not None:
            size_max = int(size_max)
            filter_conditions.append(f"size_max <= {size_max}")
        # Kết hợp các điều kiện filter bằng "and"
        filter = " and ".join(filter_conditions) if filter_conditions else None
        results_list = self.client.search(
            collection_name=self.COLLECTION_NAME,
            data=[description_vector],
            anns_field="description_vector",
            limit=top_k,
            filter=filter,
            output_fields=["*"]
        )
        all_candidates = results_list[0]
        final_results = [item["entity"] for item in all_candidates]
        return final_results

    def search_cake_by_combined_vectors(self, image_vector=None, description_vector=None, top_k=3,
                                        exclude_names: Optional[List[str]] = None, source="BonPas",
                                        recommend_cake: Optional[str] = None,
                                        price_min: Optional[float] = None,
                                        price_max: Optional[float] = None,
                                        size_min: Optional[float] = None,
                                        size_max: Optional[float] = None
                                        ):

        ranker = RRFRanker(100)
        request_image = None
        request_description = None
        filter_conditions = []

        # Thêm điều kiện exclude_names
        if exclude_names:
            filter_conditions.append(f"name NOT IN {exclude_names}")
        if recommend_cake and recommend_cake == "bánh thường":
            filter_conditions.append(
                f"NOT description LIKE '%entrement%' AND NOT description LIKE '%ánh su kem%'  AND NOT description LIKE '%rồng%' AND name NOT IN ['01212.11', '01212.15', '01212.35', '11002.1', '01212.36', '01312.6', '11002.2', '01212.38', '01212.39']")

        # Thêm điều kiện source
        filter_conditions.append(f"source == '{source}'")

        # Thêm điều kiện về price (mảng)
        if price_min is not None:
            price_min = int(price_min)
            filter_conditions.append(f"price_min >= {price_min}")
        if price_max is not None:
            price_max = int(price_max)
            filter_conditions.append(f"price_max <= {price_max}")

        # Thêm điều kiện về size (mảng)
        if size_min is not None:
            size_min = int(size_min)
            filter_conditions.append(f"size_min >= {size_min}")
        if size_max is not None:
            size_max = int(size_max)
            filter_conditions.append(f"size_max <= {size_max}")

        # Kết hợp các điều kiện filter bằng "and"
        filter = " and ".join(filter_conditions) if filter_conditions else None
        if image_vector is not None:
            search_param_image = {
                "data": [image_vector],
                "anns_field": "image_vector",
                "param": {
                    "metric_type": "COSINE",
                    "params": {"nprobe": 10}
                },
                "limit": top_k,
                "expr": filter
            }
            request_image = AnnSearchRequest(**search_param_image)
        if description_vector is not None:
            search_param_description = {
                "data": [description_vector],
                "anns_field": "description_vector",
                "param": {
                    "metric_type": "COSINE",
                    "params": {}
                },
                "limit": top_k,
                "expr": filter
            }
            request_description = AnnSearchRequest(**search_param_description)
        reqs = []
        if request_image: reqs.append(request_image)
        if request_description: reqs.append(request_description)
        # Lấy nhiều kết quả hơn ban đầu để có đủ lựa chọn sau khi lọc
        if not reqs:
            return []
        try:
            results_list = self.client.hybrid_search(
                collection_name=self.COLLECTION_NAME,
                reqs=reqs,
                output_fields=["id", "name", "image_url", "description"],
                ranker=ranker,
                limit=top_k,  # Lấy nhiều hơn ban đầu
                filter=filter
            )
        except Exception as e:
            dlog.dlog_e(f"Lỗi hybrid_search: {e}")
            return []
        if not results_list or not results_list[0]:
            return []
        all_candidates = results_list[0]
        final_results = [item["entity"] for item in all_candidates]
        return final_results

    def insert_cakes(self, cakes):
        for cake in cakes:
            if isinstance(cake["image_vector"], np.ndarray):
                cake["image_vector"] = cake["image_vector"].tolist()
            if isinstance(cake["description_vector"], np.ndarray):
                cake["description_vector"] = cake["description_vector"].tolist()
        result = self.client.insert(collection_name=self.COLLECTION_NAME, data=cakes)
        return list(result["ids"])

    def query_cakes_by_like(self, query):
        results = self.client.query(
            collection_name=self.COLLECTION_NAME,
            filter=query,
            output_fields=["name"]
        )
        return results if results else []

    def get_cakes(self, offset: int = 0, limit: int = 20, expr: str = "") -> Tuple[List[Dict[str, Any]], int]:
        """
        Lấy danh sách bánh kem theo các tiêu chí lọc
        
        Args:
            offset: Vị trí bắt đầu
            limit: Số lượng bánh trả về
            expr: Biểu thức lọc (expression filter)
            
        Returns:
            Tuple chứa danh sách bánh và tổng số bánh
        """
        try:
            if expr:
                # Nếu có biểu thức lọc
                result = self.client.query(
                    collection_name=self.COLLECTION_NAME,
                    filter=expr,
                    output_fields=["count(*)"]
                )
                total_count = result[0]['count(*)'] if result else 0

                # Lấy danh sách bánh theo biểu thức lọc
                search_results = self.client.query(
                    collection_name=self.COLLECTION_NAME,
                    filter=expr,
                    output_fields=["*"],
                    offset=offset,
                    limit=limit
                )
            else:
                # Lấy danh sách bánh theo offset, limit
                stats = self.client.get_collection_stats(collection_name=self.COLLECTION_NAME)
                total_count = int(stats["row_count"])

                search_results = self.client.query(
                    collection_name=self.COLLECTION_NAME,
                    output_fields=["*"],
                    offset=offset,
                    limit=limit
                )

            return search_results, total_count
            # return [], 0
        except Exception as e:
            traceback.print_exc()
            dlog.dlog_e(f"Error fetching cakes: {str(e)}")
            return [], 0

    def format_price_range(self, prices: List[float]) -> str:
        """
        Format giá thành dạng range
        """
        if not prices:
            return "Liên hệ"

        # Lấy giá min và max
        min_price = min(prices)
        max_price = max(prices)

        # Format số với dấu phẩy ngăn cách hàng nghìn
        def format_number(num: float) -> str:
            return "{:,.0f}đ".format(num)

        # Nếu min = max thì chỉ hiển thị 1 giá
        if min_price == max_price:
            return format_number(min_price)

        # Ngược lại hiển thị khoảng giá
        return f"{format_number(min_price)} - {format_number(max_price)}"

    def get_cake_by_id(self, cake_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết của một bánh kem theo ID
        
        Args:
            cake_id: ID của bánh kem
            
        Returns:
            Thông tin bánh kem hoặc None nếu không tìm thấy
        """

        try:
            results = self.client.query(
                collection_name=self.COLLECTION_NAME,
                ids=[int(cake_id)],
                output_fields=["*"]
            )

            return results[0] if results else None

        except Exception as e:
            traceback.print_exc()
            dlog.dlog_e(e)
            return None

    def update_cake(self, cake_id: int, cake_data: Dict[str, Any]) -> bool:
        """
        Cập nhật thông tin bánh kem
        
        Args:
            cake_id: ID của bánh kem
            cake_data: Dữ liệu bánh kem mới
            
        Returns:
            True nếu cập nhật thành công, False nếu có lỗi
        """

        try:
            # Chuyển đổi vector numpy thành list nếu cần
            if isinstance(cake_data.get("image_vector"), np.ndarray):
                cake_data["image_vector"] = cake_data["image_vector"].tolist()
            if isinstance(cake_data.get("description_vector"), np.ndarray):
                cake_data["description_vector"] = cake_data["description_vector"].tolist()
            cake_data["id"] = int(cake_id)
            cake_data["price_min"] = min(cake_data["prices"])
            cake_data["price_max"] = max(cake_data["prices"])
            sizes = extract_sizes(cake_data["form"])
            cake_data["size_min"] = min(sizes) if sizes else 0
            cake_data["size_max"] = max(sizes) if sizes else 0
            # Thêm bánh mới với ID cũ
            update_result = self.client.upsert(collection_name=self.COLLECTION_NAME, data=[cake_data])

            return update_result["upsert_count"] > 0

        except Exception as e:
            traceback.print_exc()
            dlog.dlog_e(e)
            return False

    def delete_cake(self, cake_id: str) -> bool:
        """
        Xóa bánh kem theo ID
        
        Args:
            cake_id: ID của bánh kem cần xóa
            
        Returns:
            True nếu xóa thành công, False nếu có lỗi
        """
        try:
            result = self.client.delete(collection_name=self.COLLECTION_NAME, ids=[int(cake_id)])

            return result["delete_count"] > 0

        except Exception as e:
            traceback.print_exc()
            dlog.dlog_e(e)
            return False

    def get_cakes_by_ids(self, ids: list):
        res = self.client.query(
            collection_name=self.COLLECTION_NAME,
            ids=ids,
        )

        return res

    def delete_cakes_by_filter(self, delete_filter: str):
        res = self.client.delete(
            collection_name=self.COLLECTION_NAME,
            filter=delete_filter
        )
        return res

    def get_cakes_by_names(self, cake_names):
        results = self.client.query(
            collection_name=self.COLLECTION_NAME,
            filter=f"name IN {cake_names}",
            output_fields=["*"]
        )
        if len(results) == 0:
            return None
        return results
