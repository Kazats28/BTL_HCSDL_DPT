import math
import time
from .tokenizer import tokenize
from .utils import cosine_similarity_sparse, build_query_vector

def get_matching_ids(tokens, inverted_index, max_docs):
    posting_lists = []
    for term in set(tokens):  # dùng set để tránh lặp từ
        if term in inverted_index:
            posting = set(map(int, inverted_index[term]))
            posting_lists.append((term, posting))

    if not posting_lists:
        return set()

    # Sắp xếp theo độ dài posting list tăng dần (từ ít xuất hiện đến phổ biến)
    posting_lists.sort(key=lambda x: len(x[1]))

    # Bắt đầu với intersection của các posting list ngắn nhất
    matching_ids = posting_lists[0][1].copy()

    for _, postings in posting_lists[1:]:
        matching_ids &= postings  # lấy giao nhau (intersection)
        if len(matching_ids) <= max_docs:
            break  # dừng khi còn ít văn bản phù hợp

    # Nếu quá ít, mở rộng ra bằng cách thêm union từ còn lại (tùy chọn)
    if len(matching_ids) < max_docs / 2:
        for _, postings in posting_lists:
            matching_ids |= postings
            if len(matching_ids) > max_docs:
                break

    return matching_ids

def search_query(file_path, vocab, tfidf_data, inverted_index, norm2, idf):
    start0 = time.time()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    tokens = tokenize(content)
    duration0 = time.time() - start0
    print(f"tokenize: {duration0:.2f}")

    start1 = time.time()
    query_vector = build_query_vector(tokens, vocab, idf)
    duration1 = time.time() - start1
    print(f"build_query_vector: {duration1:.3f}")

    start2 = time.time()
    # Lọc các văn bản
    # matching_ids = set()
    # for term in tokens:
    #     if term in inverted_index:
    #         matching_ids.update(map(int, inverted_index[term]))
    matching_ids = get_matching_ids(tokens, inverted_index, len(tfidf_data) * 0.9)
    duration2 = time.time() - start2
    print(f"matching_ids: {duration2:.3f}")
    print(f"len matching_ids: {len(matching_ids)}")

    start3 = time.time()
    results = []
    norm1 = math.sqrt(sum(v ** 2 for v in query_vector.values()))
    for doc_id in matching_ids:  # chỉ tính cosine với những văn bản này
        if doc_id in tfidf_data:
            doc_vector = tfidf_data[doc_id]
            score = cosine_similarity_sparse(query_vector, doc_vector, norm1, norm2[doc_id])
            if score > 0:
                results.append((doc_id, score))
    duration3 = time.time() - start3
    print(f"cosine_similarity_sparse: {duration3:.3f}")

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:3]