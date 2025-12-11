import requests
import json

# Lấy dữ liệu từ API banhkemdt.php
response = requests.get("https://doticom.vn/api/banhkemdt.php")
if response.status_code != 200:
    print("Lỗi khi lấy dữ liệu:", response.status_code)
    exit()
response.encoding = "utf-8-sig"
cakes = response.json()

# API endpoint để thêm bánh
target_url = "http://localhost:5000/cake/add-cake"

# Token API (thay 'your_token_here' bằng token thực của bạn)
token = "your_token_here"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": token
}
cake_data = {}
# Duyệt qua từng bản ghi và gửi dữ liệu
for cake in cakes:
    # Lấy dữ liệu cần thiết từ API nguồn
    name = cake.get("HinhAnh", "")  # Ví dụ: "DT00000"
    if cake.get("TenBanh") == "MTD-ST":
        continue
    # Xây dựng URL ảnh theo định dạng
    image_url = f"https://doticom.vn/lichhop/DataFile/bonpas/ImgBig/{cake.get('HinhAnh', '')}.jpg"
    # Kết hợp mô tả từ các trường có sẵn
    description = f"{cake.get('MoTa', '')}".strip()
    price = cake.get("DonGia", 0)
    # Nếu không có dữ liệu về "form" thì để rỗng hoặc giá trị mặc định
    form = cake.get('MoTa1', '')
    if name not in list(cake_data.keys()):
        payload = {
            "name": name,
            "image_url": image_url,
            "description": description,
            "price": [price],
            "form": [form],
            "source": cake.get("PhanLoai")
        }
        cake_data[name] = payload
    else:
        cake_data[name]["form"].append(form)
        cake_data[name]["price"].append(price)

for key, payload in cake_data.items():
    # Gửi POST request đến API thêm bánh
    payload["description"] = f"{payload['description']}\n Các loại bánh gồm:"
    for index, (form, price) in enumerate(zip(payload["form"],payload["price"]) ):
        payload["description"] = f"{payload['description']}\n\t Loại {index + 1}: {form} Giá: {price} VND"
    print(payload["description"])
    post_response = requests.post(target_url, headers=headers, data=json.dumps(payload))

    if post_response.status_code == 200:
        print(f"Thêm bánh {name} thành công.")
    else:
        print(f"Lỗi khi thêm bánh {name}: {post_response.status_code} - {post_response.text}")
