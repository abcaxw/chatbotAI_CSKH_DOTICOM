import pandas as pd
import httpx
from dataclasses import asdict, dataclass

import requests


# Định nghĩa class Faq
@dataclass
class Faq:
    def __init__(self, title, question, answer, source, user):
        self.title = title
        self.question = question
        self.answer = answer
        self.source = source
        self.user = user

    def to_dict(self):
        return asdict(self)

# Đọc file Excel
file_path = "/home/viettinh/Downloads/Kịch bản và từ điển trả lời khách hàng.xlsx"
sheet_name = "Từ điển sản phẩm Đồng Tiến"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Giả sử các cột trong file Excel gồm: "Tình huống", "Nguyên nhân", "Xử lý tại cửa hàng", "Ghi chú"
faqs = []
for _, row in df.iterrows():
    if pd.isnull(row["Tình huống"]):
        continue
    question = row["Tình huống"]

    answer = f"{row['Tình huống']}\nNguyên nhân: {row['Giải thích nguyên nhân']}"
    if not pd.isnull(row['Xử lý tại CH/BKR']):
        answer = f"{answer}\nXử lý tại cửa hàng: {row['Xử lý tại CH/BKR']}"
    if not pd.isnull(row['Ghi chú']):
        answer = f"{answer}\nGhi chú: {row['Ghi chú']}"
    # faq = Faq(title=question, question=question, answer=answer, source="complaint", user="admin")
    faq = {
        "title": question,
        "question": question,
        "answer": answer,
        "source": "complaint",
        "user": "admin"

    }
    faqs.append(faq)

# Gửi dữ liệu lên API
api_url = "http://localhost:5000/faq/add_faqs"  # Cập nhật URL API phù hợp
response = requests.post(api_url, json=faqs)

# Kiểm tra phản hồi từ API
print(response.status_code, response.json())