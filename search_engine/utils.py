from collections import Counter

def cosine_similarity_sparse(vec1, vec2, norm1, norm2):
    # Ưu tiên duyệt dict nhỏ hơn, xóa if nếu không ưu tiên
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1
        norm1, norm2 = norm2, norm1
    dot = sum(val * vec2.get(k, 0) for k, val in vec1.items())
    return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

def build_query_vector(tokens, vocab, idf):
    vocab_index = {term: idx for idx, term in enumerate(vocab)}
    word_count = len(tokens)
    tf = Counter(tokens)

    query_vector = {}
    for term in set(tokens):
        if term in vocab_index:
            idx = vocab_index[term]
            tf_value = tf[term] / word_count
            tfidf = tf_value * idf[term]
            if tfidf > 0:
                query_vector[str(idx)] = tfidf
    return query_vector
