import time

from PIL import Image

import dlog
from coreAI.llm.gemini_llm import gemini_1_5_flash
from dconfig import config_prompts

from bs4 import BeautifulSoup


def replace_src(html_content, img_index, replacement_text):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Tìm tất cả thẻ <img>
    img_tags = soup.find_all("img")

    # Nếu vị trí hợp lệ, thay thế thẻ <img> bằng đoạn văn bản
    if img_index < len(img_tags):
        replacement_tag = soup.new_tag("p")
        replacement_tag.string = replacement_text
        img_tags[img_index].replace_with(replacement_tag)

    return str(soup)


def remove_base64_images(html_content):
    """
    Hàm này sẽ loại bỏ các thẻ <img> có src là base64 còn sót lại
    sau khi xử lý ảnh với OCR.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all("img")
    for img_tag in img_tags:
        if img_tag.get('src', '').startswith('data:image'):
            img_tag.decompose()
    return str(soup)


def pdf2text(pdf_path):
    from pipeline.component import LoadDataComponent
    from pipeline.component.pdf_extract.extractor import PDFExtractComponent
    load_data_component = LoadDataComponent()
    dps = load_data_component.serve(pdf_path)
    pdf_extract_component = PDFExtractComponent()
    text = ""
    for dp in dps:
        pdf_extract_component.serve(dp)
        dp_text = "\n".join(text_ann.label for text_ann in dp.text_anns)

        if (not check_invalid_words(dp_text) or len(dp_text) == 0) or check_table(dp.pdf_obj):
            pil_image = Image.fromarray(dp.image)
            start_time = time.time()
            response = gemini_1_5_flash.generate_content([config_prompts.OCR_PROMPT, pil_image])

            dlog.dlog_i(f"time process LLM gemini OCR: {time.time() - start_time}")
            dp_text = response.text
        text = f"{text}\n{dp_text}"
    dlog.dlog_i(f"Extract pdf to text {text}")
    return text, dps[-1].file_name


def check_invalid_words(text):
    import re
    # Regex nhận diện từ tiếng Việt chuẩn (bao gồm chữ và dấu tiếng Việt)
    valid_word_pattern = r"[a-zA-ZÀ-ỹ0-9\-]+|[.]{2,}"
    words = text.split()
    if len(words) == 0:
        return False
    invalid_words = [word for word in words if not re.fullmatch(valid_word_pattern, word)]
    if len(invalid_words) / len(words) > 0.9:
        return False
    return True


def check_table(pdf_obj):
    blocks = pdf_obj.get("blocks", [])

    row_keys = []
    for block in blocks:
        # Chỉ xét các block chứa văn bản (không phải hình ảnh)
        if block.get("type") == 0:  # Type 0 có nghĩa là block chứa văn bản
            lines = block.get("lines", [])  # Lấy danh sách các dòng trong block
            if not lines:
                continue
            for line in lines:
                for span in line.get("spans", []):
                    x0, y0, x1, y1 = span["bbox"]
                    y0 = float(y0)
                    row_key = round(y0, 1)
                    row_keys.append(row_key)

    if len(row_keys) < 2:
        return False  # Nếu không có đủ dữ liệu để xác định bảng, trả về False

        # Sắp xếp row_keys và kiểm tra sự khác biệt giữa các row_key
    row_keys.sort()
    differences = [row_keys[i + 1] - row_keys[i] for i in range(len(row_keys) - 1)]

    # Nếu sự khác biệt giữa các row_keys là nhỏ, có thể là bảng
    threshold = 0.2  # Ngưỡng để xác định sự thay đổi nhỏ giữa các hàng
    if all(diff < threshold for diff in differences):
        return True
    else:
        return False
