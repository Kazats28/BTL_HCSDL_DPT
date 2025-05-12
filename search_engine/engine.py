import math
import time
from .tokenizer import tokenize
from .utils import cosine_similarity_sparse, build_query_vector
from nltk.corpus import wordnet
from nltk import pos_tag, word_tokenize
import nltk
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger_eng')
# nltk.download('punkt')

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

def get_wordnet_synonyms(token, pos):
    """Lấy từ đồng nghĩa từ WordNet dựa trên loại từ (POS)."""
    # Chuyển POS tag của NLTK sang WordNet
    pos_map = {'NN': 'n', 'VB': 'v', 'JJ': 'a', 'RB': 'r'}
    wn_pos = pos_map.get(pos[:2], None)
    if not wn_pos:
        return []

    synonyms = set()
    for syn in wordnet.synsets(token, pos=wn_pos):
        for lemma in syn.lemmas():
            synonym = lemma.name().lower().replace('_', '-')
            if synonym != token and '-' not in synonym:  # Loại bỏ từ gốc và từ ghép
                synonyms.add(synonym)
    return list(synonyms)

def search_query(file_path, vocab, tfidf_data, inverted_index, norm2, idf):
    start0 = time.time()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    tokens = tokenize(content)
    # POS tagging để xác định loại từ
    # pos_tags = pos_tag(tokens)
    # for token, pos in pos_tags:
    #     if pos.startswith(('NN', 'VB', 'JJ', 'RB')):  # Chỉ mở rộng danh từ, động từ, tính từ, trạng từ
    #         synonyms = get_wordnet_synonyms(token, pos)
    #         for syn in synonyms[:3]:  # Giới hạn tối đa 3 từ đồng nghĩa mỗi từ
    #             tokens.append(syn)
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
# import math
# import time
# from .tokenizer import tokenize
# from .utils import cosine_similarity_sparse, build_query_vector
# from nltk.corpus import wordnet
# from nltk import pos_tag, word_tokenize
# import nltk
#
# def get_matching_ids(tokens, inverted_index, max_docs):
#     posting_lists = []
#     for term in set(tokens):  # dùng set để tránh lặp từ
#         if term in inverted_index:
#             posting = set(map(int, inverted_index[term]))
#             posting_lists.append((term, posting))
#
#     if not posting_lists:
#         return set()
#
#     # Sắp xếp theo độ dài posting list tăng dần
#     posting_lists.sort(key=lambda x: len(x[1]))
#
#     # Bắt đầu với intersection của các posting list ngắn nhất
#     matching_ids = posting_lists[0][1].copy()
#
#     for _, postings in posting_lists[1:]:
#         matching_ids &= postings
#         if len(matching_ids) <= max_docs:
#             break
#
#     # Nếu quá ít, mở rộng bằng union
#     if len(matching_ids) < max_docs / 2:
#         for _, postings in posting_lists:
#             matching_ids |= postings
#             if len(matching_ids) > max_docs:
#                 break
#
#     return matching_ids
#
# def get_wordnet_synonyms(token, pos):
#     """Lấy từ đồng nghĩa từ WordNet dựa trên loại từ (POS)."""
#     # Chuyển POS tag của NLTK sang WordNet
#     pos_map = {'NN': 'n', 'VB': 'v', 'JJ': 'a', 'RB': 'r'}
#     wn_pos = pos_map.get(pos[:2], None)
#     if not wn_pos:
#         return []
#
#     synonyms = set()
#     for syn in wordnet.synsets(token, pos=wn_pos):
#         for lemma in syn.lemmas():
#             synonym = lemma.name().lower().replace('_', '-')
#             if synonym != token and '-' not in synonym:  # Loại bỏ từ gốc và từ ghép
#                 synonyms.add(synonym)
#     return list(synonyms)
#
# def search_query(file_path, vocab, tfidf_data, inverted_index, norm2, idf):
#     start0 = time.time()
#     with open(file_path, "r", encoding="utf-8") as f:
#         content = f.read()
#     tokens = tokenize(content)
#     duration0 = time.time() - start0
#     print(f"tokenize: {duration0:.2f}")
#
#     # Mở rộng truy vấn với từ đồng nghĩa
#     start_exp = time.time()
#     weighted_tokens = []
#     # POS tagging để xác định loại từ
#     pos_tags = pos_tag(tokens)
#     for token, pos in pos_tags:
#         weighted_tokens.append((token, 1.0))  # Từ gốc có trọng số 1.0
#         if pos.startswith(('NN', 'VB', 'JJ', 'RB')):  # Chỉ mở rộng danh từ, động từ, tính từ, trạng từ
#             synonyms = get_wordnet_synonyms(token, pos)
#             for syn in synonyms[:3]:  # Giới hạn tối đa 3 từ đồng nghĩa mỗi từ
#                 weighted_tokens.append((syn, 0.5))  # Từ đồng nghĩa có trọng số 0.5
#     duration_exp = time.time() - start_exp
#     print(f"query_expansion: {duration_exp:.3f}")
#
#     start1 = time.time()
#     query_vector = build_query_vector(weighted_tokens, vocab, idf)
#     duration1 = time.time() - start1
#     print(f"build_query_vector: {duration1:.3f}")
#
#     start2 = time.time()
#     # Lấy các tài liệu phù hợp
#     all_tokens = [token for token, _ in weighted_tokens]
#     matching_ids = get_matching_ids(all_tokens, inverted_index, len(tfidf_data) * 0.9)
#     duration2 = time.time() - start2
#     print(f"matching_ids: {duration2:.3f}")
#     print(f"len matching_ids: {len(matching_ids)}")
#
#     start3 = time.time()
#     results = []
#     norm1 = math.sqrt(sum(v ** 2 for v in query_vector.values()))
#     for doc_id in matching_ids:
#         if doc_id in tfidf_data:
#             doc_vector = tfidf_data[doc_id]
#             score = cosine_similarity_sparse(query_vector, doc_vector, norm1, norm2[doc_id])
#             if score > 0:
#                 results.append((doc_id, score))
#     duration3 = time.time() - start3
#     print(f"cosine_similarity_sparse: {duration3:.3f}")
#
#     results.sort(key=lambda x: x[1], reverse=True)
#     return results[:3]