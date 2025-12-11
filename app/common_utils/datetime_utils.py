from datetime import datetime, timedelta

from common_utils.constants import DAY_MAP


def get_current_date_info():
    now = datetime.now()

    # Biến chứa ngày hiện tại theo định dạng YYYY-MM-DD
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    day_of_week = DAY_MAP.get(now.strftime("%A"), "Unknown")
    return current_time, day_of_week


def calculate_receive_time(order_dt: datetime) -> datetime:
    """
    Tính thời điểm bánh phổ thông sẵn sàng theo quy tắc:
    - Thời gian nhận đơn: 7h-11h30, 12h30-16h
    - Thời gian hoàn thành: 3 tiếng trong giờ nhận đơn
    - Nếu đặt ngoài giờ nhận đơn (16h-7h hôm sau) → nhận bánh sớm nhất 10h hôm sau
    - Nếu quá trình làm bánh đi qua giờ nghỉ trưa 11h30-12h30 thì cộng thêm 1 tiếng bù
    """
    hour = order_dt.hour + order_dt.minute / 60.0

    # Ngoài giờ nhận đơn: 16h-7h hôm sau
    if hour >= 16 or hour < 7:
        # Tính ngày nhận bánh
        if hour >= 16:
            # Đặt sau 16h hôm nay -> nhận 10h hôm sau
            receive_date = order_dt.date() + timedelta(days=1)
        else:
            # Đặt từ 0h-7h -> nhận 10h cùng ngày
            receive_date = order_dt.date()

        return datetime.combine(receive_date, datetime.min.time()).replace(hour=10, minute=0)

    # Trong giờ nhận đơn: 7h-11h30, 12h30-16h
    # Cộng 3 tiếng và kiểm tra có đi qua giờ nghỉ trưa không
    ready_time = order_dt + timedelta(hours=3)

    # Kiểm tra nếu quá trình làm bánh đi qua giờ nghỉ trưa (11h30-12h30)
    order_hour = order_dt.hour + order_dt.minute / 60.0
    ready_hour = ready_time.hour + ready_time.minute / 60.0

    # Nếu bắt đầu trước 11h30 và kết thúc sau 11h30,
    # hoặc bắt đầu trước 12h30 và kết thúc sau 12h30
    # thì có nghĩa là quá trình làm bánh đi qua thời gian nghỉ trưa
    lunch_start = 11.5  # 11h30
    lunch_end = 12.5  # 12h30

    if (order_hour < lunch_end and ready_hour > lunch_start):
        # Quá trình làm bánh có đi qua giờ nghỉ trưa -> cộng thêm 1 tiếng bù
        ready_time = ready_time + timedelta(hours=1)

    return ready_time


def calculate_receive_time_special(order_dt: datetime) -> datetime:
    """
    Tính thời điểm bánh đặc biệt sẵn sàng theo quy tắc:
    - Chốt đơn lúc 9h hàng ngày
    - Nếu đặt trước 9h → nhận 16h cùng ngày
    - Nếu đặt từ 9h trở đi → nhận 16h ngày hôm sau
    """
    hour = order_dt.hour + order_dt.minute / 60.0

    if hour < 9:
        # Đặt trước 9h -> nhận 16h cùng ngày
        return order_dt.replace(hour=16, minute=0, second=0, microsecond=0)
    else:
        # Đặt từ 9h trở đi -> nhận 16h ngày hôm sau
        next_day = order_dt.date() + timedelta(days=1)
        return datetime.combine(next_day, datetime.min.time()).replace(hour=16, minute=0)


def time_until_pickup(order_dt: datetime, is_special: bool = False) -> timedelta:
    """
    Tính khoảng thời gian từ thời điểm hiện tại đến khi có thể nhận bánh.

    Args:
        order_dt: Thời điểm đặt hàng
        is_special: True nếu là bánh đặc biệt, False nếu là bánh phổ thông
    """
    if is_special:
        ready = calculate_receive_time_special(order_dt)
    else:
        ready = calculate_receive_time(order_dt)

    now = datetime.now()
    return ready - now


def is_valid_receive_time_cake_normal(requested_time_str: str, now_dt: datetime):
    """
    Kiểm tra xem thời gian yêu cầu nhận bánh phổ thông có hợp lệ hay không.
    Trả về True nếu requested_time >= thời gian tối thiểu có bánh.
    """
    requested_dt = datetime.strptime(requested_time_str, "%Y-%m-%d %H:%M")
    min_ready_time = calculate_receive_time(now_dt)
    return requested_dt >= min_ready_time, min_ready_time


def is_valid_receive_time_cake_special(requested_time_str: str, now_dt: datetime):
    """
    Kiểm tra xem thời gian yêu cầu nhận bánh đặc biệt có hợp lệ hay không.
    Trả về True nếu requested_time >= thời gian tối thiểu có bánh.
    """
    requested_dt = datetime.strptime(requested_time_str, "%Y-%m-%d %H:%M")
    min_ready_time = calculate_receive_time_special(now_dt)
    return requested_dt >= min_ready_time, min_ready_time


def get_working_hours_info():
    """
    Trả về thông tin giờ làm việc của phòng bánh kem.
    """
    return {
        "order_receiving_hours": "7h-11h30, 12h30-16h",
        "lunch_break": "11h30-12h30",
        "special_cake_cutoff": "9h (chốt đơn bánh đặc biệt)",
        "normal_cake_min_time": "3 tiếng + 1 tiếng bù nếu qua giờ nghỉ trưa",
        "special_cake_delivery": "16h cùng ngày (nếu đặt trước 9h) hoặc 16h ngày hôm sau"
    }