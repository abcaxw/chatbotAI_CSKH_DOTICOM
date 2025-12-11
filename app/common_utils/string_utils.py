from __future__ import print_function

import ast
import re
from difflib import SequenceMatcher

from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from unidecode import unidecode

from common_utils.constants import OPEN_CLOSE_BRACKET_REGREX, ROMAN_NUMERAL_INDEX_REGREX, BULLET_POINT_RE, OCR_VOCAB_RE


def normalize_str(string, ignore_str=None,
                  remove_digit=False,
                  remove_roman_numeral=False,
                  remove_alphabet_numbering=False,
                  remove_open_close_bracket=False,
                  min_len=None, keep_space=False):
    if ignore_str is None:
        ignore_str = []
    if string is None:
        return None
    if ignore_str:
        for s in ignore_str:
            if s in string:
                string = string.replace(s, "").strip()
    if min_len:
        string = " ".join([w for w in string.split(" ") if len(w) >= min_len])

    string = unidecode(string.lower())

    if remove_roman_numeral:
        string = re.sub(ROMAN_NUMERAL_INDEX_REGREX, ' ', string)
    if remove_alphabet_numbering:
        string = re.sub('^[a-f]{1}\. ', ' ', string)
    if remove_open_close_bracket:
        string = re.sub(OPEN_CLOSE_BRACKET_REGREX, ' ', string)

    if remove_digit:
        string = re.sub('[^a-zA-Z]', ' ', string)
    else:
        string = re.sub('[^a-zA-Z0-9]', ' ', string)

    if not keep_space:
        string = re.sub(' +', ' ', string)
    return string.strip().replace("/", " ")


def is_bullet_point(text):
    return re.match(BULLET_POINT_RE, text.strip())


def is_vietnamese(text):
    return re.match(OCR_VOCAB_RE, text)


def find_match_percentage(key_word, text):
    ratio = SequenceMatcher(None, key_word, text).ratio()
    if ratio >= 0.9:
        return ""
    key_len = len(key_word.split())
    text_len = len(text.split())
    if text_len >= key_len:
        compare_str = " ".join(text.split()[0: key_len])
        ratio = SequenceMatcher(None, key_word, compare_str).ratio()
        if ratio >= 0.9:
            return " ".join(text.split()[key_len:])
    return None


def remove_accents(input_str):
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    s = ''
    input_str.encode('utf-8')
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s


def similar(a, b):
    if a is None or b is None:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def remove_punctuation(input_string):
    input_string = re.sub(r'[^\w\s\.\:\-\/\(\)\@\_\+,]', ' ', input_string)
    return input_string


def clean_text(text):
    text = re.sub(r'[^\w\s]', " ", text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def standardize_text(input_string):
    input_string = remove_punctuation(input_string)
    input_string = re.sub(r'\s+', ' ', input_string)
    input_string = input_string.strip()
    return input_string


def clean_space(text):
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'(^ )|( $)', '', text)
    text = text.replace(' \n ', '\n').replace(' \n', '\n').replace('\n ', '\n')
    return text


def get_title_min_error(titles):
    titles = sorted(titles, key=lambda x: x[list(x.keys())[0]])
    return list(titles[0].keys())[0]


def find_contain_arr(text, arr, ignore_space=False):
    text = normalize_str(text).replace(" ", "") if ignore_space else normalize_str(text)
    for item in arr:
        norm = normalize_str(item).replace(" ", "") if ignore_space else normalize_str(item)
        if norm in text:
            return item
    return None


def check_int(s):
    try:
        if str(s).isdigit():
            value = int(s)
            return value, True
        return s, False
    except ValueError:
        return s, False


def check_float(s):
    if s is None:
        return None, False
    try:
        value = float(s)
        return value, True
    except ValueError:
        return s, False


def convert_number_value(s):
    if s is not None:
        s = str(s).replace(".", "").replace(",", ".").replace(" ", "")
        int_value, check = check_int(s)
        if check:
            return int_value
        else:
            float_value, check = check_float(s)
            if check:
                return float_value
        return s
    return None


def convert_number_value_quantity(s):
    if s is not None:
        int_value, check = check_int(s)
        if check:
            return int_value
        s = str(s).replace(",", ".")
        int_value, check = check_int(s)
        if check:
            return int_value
        else:
            float_value, check = check_float(s)
            if check:
                return float_value
        return s
    return None


def remove_accents_string(input_str):
    if input_str is None:
        return None
    return unidecode(input_str)


def text2chunks(text, chunk_size=250, chunk_overlap=30, headers_to_split_on=None):
    if headers_to_split_on is None:
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(text)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    splits = text_splitter.split_documents(md_header_splits)
    return splits

def tach_chuoi_theo_url(text):
  """Tách chuỗi thành các đoạn ngăn cách bởi URL http://.

  Args:
    text: Chuỗi đầu vào.

  Returns:
    Một danh sách các chuỗi đã được tách.
  """
  # Sử dụng regular expression để tìm và tách chuỗi tại các URL bắt đầu bằng http://
  parts = re.split(r'(https?://\S+\.(?:jpg|jpeg|png))', text)
  return parts

def extract_sizes(size_list_raw):
    try:
        size_list = ast.literal_eval(size_list_raw) if isinstance(size_list_raw, str) else size_list_raw
        if not isinstance(size_list, list):
            return []
        return [
            int(m)
            for s in size_list
            for m in re.findall(r"[Kk]ích\s*(\d+)", s, re.IGNORECASE)
        ]
    except Exception as e:
        print(f"Lỗi khi parse sizes: {e}")
        return []