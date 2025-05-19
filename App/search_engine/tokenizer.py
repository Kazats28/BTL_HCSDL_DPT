import re
from .stemmer import PorterStemmer
# Đọc danh sách stopwords từ file
with open("stopwords.txt", "r", encoding="utf-8") as f:
    STOPWORDS = set(f.read().splitlines())

stemmer = PorterStemmer()

def tokenize(text):
    # Loại bỏ ký tự đặc biệt, giữ lại chữ, số, dấu gạch ngang và khoảng trắng
    text = re.sub(r'[^\w\s-]', '', text)
    # Chuyển về chữ thường và tách từ bằng khoảng trắng
    tokens = text.lower().split()
    # Xử lý tokens
    processed_tokens = []
    for token in tokens:
        # Loại bỏ các cụm có hai dấu gạch ngang trở lên
        if re.search(r'-{2,}', token):
            continue
        # Loại bỏ dấu gạch ngang ở đầu và cuối từ
        token = re.sub(r'^-+|-+$', '', token)
        token = re.sub(r'^_+|_+$', '', token)
        # Kiểm tra stopword sau khi xử lý
        if token and token not in STOPWORDS:
            tok = stemmer.stem(token)
            processed_tokens.append(tok)

    return processed_tokens