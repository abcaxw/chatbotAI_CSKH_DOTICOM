import json
from time import time

import dlog
from database.dao.milvus.bill_dao import BillDAO


def get_bills_by_customer_id(customer_id, limit: int = 5):
    dlog.dlog_i(f"---GET cake by ID: {customer_id}")
    bill_dao = BillDAO()
    filter = f"customer_id == {customer_id}"
    output_fields = ["*"]
    bills = bill_dao.get_bills_by_customer(filter, output_fields, limit)
    return bills


def insert_bill(order_cakes_information, total_price, customer_id, bill_id):
    created_at = int(time())
    bill_data = {
        "bill_id": bill_id,
        "customer_id": customer_id,
        "vector": [0.1, 0.2],
        "cakes_order": [json.dumps(cake, ensure_ascii=False) for cake in order_cakes_information],
        "total_price": total_price,
        "description": "Order for birthday party",
        "status_order": 0,
        "status_payment": 0,
        "status_shipping": 0,
        "created_at": created_at,
        "update_at": created_at
    }

    bill_dao = BillDAO()
    res = bill_dao.insert_bill(bill_data)
    return res


def update_bill(order_cakes_information, total_price, customer_id, bill_id):
    filter = f"bill_id == {bill_id} AND customer_id == {customer_id}"

    bill_dao = BillDAO()
    bill = bill_dao.get_bills_by_customer(filter, ["*"])
    if len(bill) == 0:
        insert_bill(order_cakes_information, total_price, customer_id, bill_id)
    else:
        bill_data = bill[-1]
        bill_data["cakes_order"] = [json.dumps(cake, ensure_ascii=False) for cake in order_cakes_information]
        bill_data["total_price"] = total_price
        res = bill_dao.insert_bill(bill_data)
    return f"Mã {bill_id} đã cập nhật thành công"

