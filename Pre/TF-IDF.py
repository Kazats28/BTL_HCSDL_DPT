import os
import math
import time
import re
from tqdm import tqdm
from collections import defaultdict, Counter

from search_engine.save_json import save_json
from search_engine.stemmer import PorterStemmer
from search_engine.save_pkl import save_pkl
from search_engine.load_pkl import load_pkl

FOLDER_PATH = "data"
DEFAULT_PATH = "../App/File"
DOC_FILE = DEFAULT_PATH + "/" + "documents"
FILE_FILE = DEFAULT_PATH + "/" + "filenames"
IDF_FILE = DEFAULT_PATH +  "/" + "idf"
METADATA_FILE = DEFAULT_PATH + "/" + "metadata"
VOCAB_FILE = DEFAULT_PATH + "/" + "vocab"
TFIDF_FILE = DEFAULT_PATH + "/" + "tf-idf"
INVERTED_INDEX_FILE = DEFAULT_PATH + "/" + "inverted_index"

os.makedirs(DEFAULT_PATH, exist_ok=True)

stemmer = PorterStemmer()

# Đọc danh sách stopwords từ file
with open("stopwords.txt", "r", encoding="utf-8") as f:
    STOPWORDS = set(f.read().splitlines())

start_time = time.time()

# === Kiểm tra và nạp dữ liệu nếu đã tồn tại ===
if os.path.exists(DOC_FILE + ".pkl") and os.path.exists(FILE_FILE + ".pkl"):
    print("Tải lại documents và filenames từ file lưu...")
    documents = load_pkl(DOC_FILE)
    filenames = load_pkl(FILE_FILE)
else:
    print("Đọc và xử lý văn bản từ thư mục...")
    documents = []
    filenames = []
    for file in tqdm(os.listdir(FOLDER_PATH)):
        if file.endswith(".txt"):
            filepath = os.path.join(FOLDER_PATH, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                print(f"Lỗi đọc file (không phải UTF-8): {filepath}")
                continue
            content = re.sub(r'[^\w\s-]', '', content)
            tokens = content.lower().split()
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
            documents.append(processed_tokens)
            filenames.append(os.path.relpath(filepath, FOLDER_PATH))

    # Lưu lại để tái sử dụng
    save_pkl(DOC_FILE, documents)
    save_pkl(FILE_FILE, filenames)

# === Bước 1: Xây chỉ mục ngược (Inverted Index) ===
print("Xây dựng inverted index để tính DF nhanh...")
inverted_index = defaultdict(set)
vocab = set()
for doc_id, doc in enumerate(tqdm(documents)):
    unique_terms = set(doc)
    vocab.update(unique_terms)
    for term in unique_terms:
        inverted_index[term].add(doc_id)

vocab = sorted(vocab)

# === Bước 2: Tính IDF từ inverted index ===
print("Tính IDF cho từng từ...")
N = len(documents)
idf = {term: math.log(N / (1 + len(inverted_index[term]))) for term in vocab}
save_pkl(IDF_FILE, idf)
save_json(IDF_FILE, idf)

# === Bước 3: Tính TF-IDF từng văn bản và lưu metadata ===
print("Tính TF-IDF và lưu metadata...")
metadata = []
tfidf_data = []

for doc_id in tqdm(range(N)):
    doc = documents[doc_id]
    filename = filenames[doc_id]
    filepath = os.path.join(FOLDER_PATH, filename)
    word_count = len(doc)
    tf = Counter(doc)

    tfidf_vector = []
    for term in vocab:
        if tf[term] > 0:
            tf_value = 1 + math.log(tf[term])  # TF log scale
        else:
            tf_value = 0
        tfidf = tf_value * idf[term]
        tfidf_vector.append(tfidf)

    metadata.append({
        "doc_id": doc_id,
        "filename": filename,
        "word_count": word_count,
        "filepath": os.path.abspath(filepath)
    })

    tfidf_data.append({
        "doc_id": doc_id,
        "vector_sparse": {str(i): tfidf_vector[i] for i in range(len(tfidf_vector)) if tfidf_vector[i] > 0}
    })

# === Bước 4: Ghi metadata ra file ===
print("Ghi metadata vào file...")
save_pkl(METADATA_FILE, metadata)
save_json(METADATA_FILE, metadata)

# === Bước 5: Ghi TF-IDF vector ra file ===
print("Ghi TF-IDF vector vào file...")
save_pkl(TFIDF_FILE, tfidf_data)
save_json(TFIDF_FILE, tfidf_data)

# === Bước 6: Ghi từ điển vocab vào file ===
print("Ghi từ điển vocab vào file...")
save_pkl(VOCAB_FILE, vocab)
save_json(VOCAB_FILE, vocab)

# === Bước 7: Ghi chỉ mục ngược với doc_id ===
print("Ghi chỉ mục ngược vào file...")
inverted_index_doc_ids = {term: sorted(list(doc_ids)) for term, doc_ids in inverted_index.items()}

save_pkl(INVERTED_INDEX_FILE, inverted_index_doc_ids)
save_json(INVERTED_INDEX_FILE, inverted_index_doc_ids)

elapsed = time.time() - start_time
print(f"Hoàn thành. Thời gian: {elapsed:.2f} giây.")