def round_to(x, det=4, is_up=False, is_down=False):
    if is_up:
        return round(abs(x) * (10 ** det)) / (10 ** det)
    elif is_down:
        return int(abs(x) * (10 ** det)) / (10 ** det)
    return round(abs(x), det)
