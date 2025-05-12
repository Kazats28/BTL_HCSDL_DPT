import os
import math
import json
import time
import pickle
import re
from tqdm import tqdm
from collections import defaultdict, Counter

FOLDER_PATH = "Text"
DOC_FILE = "File/documents.pkl"
FILE_FILE = "File/filenames.pkl"
IDF_FILE = "File/idf.pkl"
METADATA_FILE = "File/metadata.pkl"
VOCAB_FILE = "File/vocab.pkl"
TFIDF_FILE = "File/tf-idf.pkl"
INVERTED_INDEX_FILE = "File/inverted_index.pkl"

os.makedirs("File", exist_ok=True)

# Đọc danh sách stopwords từ file
with open("stopwords.txt", "r", encoding="utf-8") as f:
    STOPWORDS = set(f.read().splitlines())

start_time = time.time()

# === Kiểm tra và nạp dữ liệu nếu đã tồn tại ===
if os.path.exists(DOC_FILE) and os.path.exists(FILE_FILE):
    print("Tải lại documents và filenames từ file lưu...")
    with open(DOC_FILE, "rb") as f:
        documents = pickle.load(f)
    with open(FILE_FILE, "rb") as f:
        filenames = pickle.load(f)
else:
    print("Đọc và xử lý văn bản từ thư mục...")
    documents = []
    filenames = []
    for file in tqdm(os.listdir(FOLDER_PATH)):
        if file.endswith(".txt"):
            filepath = os.path.join(FOLDER_PATH, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Loại bỏ ký tự đặc biệt, giữ lại chữ, số, dấu gạch ngang và khoảng trắng
                content = re.sub(r'[^\w\s-]', '', content)
                # Chuyển về chữ thường và tách từ bằng khoảng trắng
                tokens = content.lower().split()
                # Xử lý tokens
                processed_tokens = []
                for token in tokens:
                    # Loại bỏ các cụm có hai dấu gạch ngang trở lên
                    if re.search(r'-{2,}', token):
                        continue
                    # Loại bỏ dấu gạch ngang ở đầu và cuối từ
                    token = re.sub(r'^-+|-+$', '', token)
                    # Kiểm tra stopword sau khi xử lý
                    if token and token not in STOPWORDS:
                        processed_tokens.append(token)
                documents.append(processed_tokens)
                filenames.append(file)

    # Lưu lại để tái sử dụng
    with open(DOC_FILE, "wb") as f:
        pickle.dump(documents, f)
    with open(FILE_FILE, "wb") as f:
        pickle.dump(filenames, f)

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
with open(IDF_FILE, "wb") as f:
    pickle.dump(idf, f)

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

    # tfidf_vector = []
    # for term in vocab:
    #     tf_value = tf[term] / word_count if word_count > 0 else 0
    #     tfidf = tf_value * idf[term]
    #     tfidf_vector.append(tfidf)
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
        "filepath": filepath
    })

    tfidf_data.append({
        "doc_id": doc_id,
        "vector_sparse": {str(i): tfidf_vector[i] for i in range(len(tfidf_vector)) if tfidf_vector[i] > 0}
    })

# === Bước 4: Ghi metadata ra file ===
print("Ghi metadata vào file...")
with open(METADATA_FILE, "wb") as f:
    pickle.dump(metadata, f)

# === Bước 5: Ghi TF-IDF vector ra file ===
print("Ghi TF-IDF vector vào file...")
with open(TFIDF_FILE, "wb") as f:
    pickle.dump(tfidf_data, f)

# === Bước 6: Ghi từ điển vocab vào file ===
print("Ghi từ điển vocab vào file...")
with open(VOCAB_FILE, "wb") as f:
    pickle.dump(vocab, f)
with open("File/vocab.json", "w", encoding="utf-8") as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

# === Bước 7: Ghi chỉ mục ngược với doc_id ===
print("Ghi chỉ mục ngược vào file...")
inverted_index_doc_ids = {term: sorted(list(doc_ids)) for term, doc_ids in inverted_index.items()}

with open(INVERTED_INDEX_FILE, "wb") as f:
    pickle.dump(inverted_index_doc_ids, f)

elapsed = time.time() - start_time
print(f"Hoàn thành. Thời gian: {elapsed:.2f} giây.")
# import os
# import math
# import json
# import time
# import pickle
# import re
# from tqdm import tqdm
# from collections import defaultdict, Counter
# from nltk.corpus import wordnet
# from nltk import pos_tag, word_tokenize
# import nltk
#
# FOLDER_PATH = "Text"
# DOC_FILE = "documents.pkl"
# FILE_FILE = "filenames.pkl"
# IDF_FILE = "idf.pkl"
# METADATA_FILE = "metadata.pkl"
# VOCAB_FILE = "vocab.pkl"
# TFIDF_FILE = "tf-idf.pkl"
# INVERTED_INDEX_FILE = "inverted_index.pkl"
#
# # Đọc danh sách stopwords từ file
# with open("stopwords.txt", "r", encoding="utf-8") as f:
#     STOPWORDS = set(f.read().splitlines())
#
#
# def get_wordnet_synonyms(token, pos):
#     """Lấy từ đồng nghĩa từ WordNet dựa trên loại từ (POS)."""
#     pos_map = {'NN': 'n', 'VB': 'v', 'JJ': 'a', 'RB': 'r'}
#     wn_pos = pos_map.get(pos[:2], None)
#     if not wn_pos:
#         return []
#
#     synonyms = set()
#     for syn in wordnet.synsets(token, pos=wn_pos):
#         for lemma in syn.lemmas():
#             synonym = lemma.name().lower().replace('_', '-')
#             if synonym != token and '-' not in synonym:
#                 synonyms.add(synonym)
#     return list(synonyms)
#
#
# start_time = time.time()
#
# # === Kiểm tra và nạp dữ liệu nếu đã tồn tại ===
# if os.path.exists(DOC_FILE) and os.path.exists(FILE_FILE):
#     print("Tải lại documents và filenames từ file lưu...")
#     with open(DOC_FILE, "rb") as f:
#         documents = pickle.load(f)
#     with open(FILE_FILE, "rb") as f:
#         filenames = pickle.load(f)
# else:
#     print("Đọc và xử lý văn bản từ thư mục...")
#     documents = []
#     filenames = []
#     for file in tqdm(os.listdir(FOLDER_PATH)):
#         if file.endswith(".txt"):
#             filepath = os.path.join(FOLDER_PATH, file)
#             with open(filepath, "r", encoding="utf-8") as f:
#                 content = f.read()
#                 # Loại bỏ ký tự đặc biệt, giữ lại chữ, số, dấu gạch ngang và khoảng trắng
#                 content = re.sub(r'[^\w\s-]', '', content)
#                 # Chuyển về chữ thường và tách từ bằng khoảng trắng
#                 tokens = content.lower().split()
#                 # Xử lý tokens
#                 processed_tokens = []
#                 for token in tokens:
#                     # Loại bỏ các cụm có hai dấu gạch ngang trở lên
#                     if re.search(r'-{2,}', token):
#                         continue
#                     # Loại bỏ dấu gạch ngang ở đầu và cuối từ
#                     token = re.sub(r'^-+|-+$', '', token)
#                     # Kiểm tra stopword sau khi xử lý
#                     if token and token not in STOPWORDS:
#                         processed_tokens.append(token)
#
#                 # Mở rộng từ đồng nghĩa
#                 weighted_tokens = []
#                 pos_tags = pos_tag(processed_tokens)
#                 for token, pos in pos_tags:
#                     weighted_tokens.append((token, 1.0))  # Từ gốc có trọng số 1.0
#                     if pos.startswith(('NN', 'VB', 'JJ', 'RB')):
#                         synonyms = get_wordnet_synonyms(token, pos)[:3]  # Giới hạn 3 từ đồng nghĩa
#                         for syn in synonyms:
#                             weighted_tokens.append((syn, 0.5))  # Từ đồng nghĩa có trọng số 0.5
#
#                 documents.append(weighted_tokens)
#                 filenames.append(file)
#
#     # Lưu lại để tái sử dụng
#     with open(DOC_FILE, "wb") as f:
#         pickle.dump(documents, f)
#     with open(FILE_FILE, "wb") as f:
#         pickle.dump(filenames, f)
#
# # === Bước 1: Xây chỉ mục ngược (Inverted Index) ===
# print("Xây dựng inverted index để tính DF nhanh...")
# inverted_index = defaultdict(set)
# vocab = set()
# for doc_id, doc in enumerate(tqdm(documents)):
#     unique_terms = set(token for token, _ in doc)  # Lấy tập hợp từ duy nhất
#     vocab.update(unique_terms)
#     for term in unique_terms:
#         inverted_index[term].add(doc_id)
#
# vocab = sorted(vocab)
#
# # === Bước 2: Tính IDF từ inverted index ===
# print("Tính IDF cho từng từ...")
# N = len(documents)
# idf = {term: math.log(N / (1 + len(inverted_index[term]))) for term in vocab}
# with open(IDF_FILE, "wb") as f:
#     pickle.dump(idf, f)
#
# # === Bước 3: Tính TF-IDF từng văn bản và lưu metadata ===
# print("Tính TF-IDF và lưu metadata...")
# metadata = []
# tfidf_data = []
#
# for doc_id in tqdm(range(N)):
#     doc = documents[doc_id]
#     filename = filenames[doc_id]
#     filepath = os.path.join(FOLDER_PATH, filename)
#     total_weight = sum(weight for _, weight in doc)  # Tổng trọng số (dùng cho metadata)
#     tf = Counter()
#     for token, weight in doc:
#         tf[token] += weight  # Tính tổng trọng số cho mỗi từ
#
#     tfidf_vector = []
#     for term in vocab:
#         if tf[term] > 0:
#             tf_value = 1 + math.log(tf[term])  # TF log scale
#         else:
#             tf_value = 0
#         tfidf = tf_value * idf[term]
#         tfidf_vector.append(tfidf)
#
#     metadata.append({
#         "doc_id": doc_id,
#         "filename": filename,
#         "word_count": total_weight,  # Lưu tổng trọng số
#         "filepath": filepath
#     })
#
#     tfidf_data.append({
#         "doc_id": doc_id,
#         "vector_sparse": {str(i): tfidf_vector[i] for i in range(len(tfidf_vector)) if tfidf_vector[i] > 0}
#     })
#
# # === Bước 4: Ghi metadata ra file ===
# print("Ghi metadata vào file...")
# with open(METADATA_FILE, "wb") as f:
#     pickle.dump(metadata, f)
#
# # === Bước 5: Ghi TF-IDF vector ra file ===
# print("Ghi TF-IDF vector vào file...")
# with open(TFIDF_FILE, "wb") as f:
#     pickle.dump(tfidf_data, f)
#
# # === Bước 6: Ghi từ điển vocab vào file ===
# print("Ghi từ điển vocab vào file...")
# with open(VOCAB_FILE, "wb") as f:
#     pickle.dump(vocab, f)
# with open("vocab.json", "w", encoding="utf-8") as f:
#     json.dump(vocab, f, ensure_ascii=False, indent=2)
#
# # === Bước 7: Ghi chỉ mục ngược với doc_id ===
# print("Ghi chỉ mục ngược vào file...")
# inverted_index_doc_ids = {term: sorted(list(doc_ids)) for term, doc_ids in inverted_index.items()}
#
# with open(INVERTED_INDEX_FILE, "wb") as f:
#     pickle.dump(inverted_index_doc_ids, f)
#
# elapsed = time.time() - start_time
# print(f"Hoàn thành. Thời gian: {elapsed:.2f} giây.")