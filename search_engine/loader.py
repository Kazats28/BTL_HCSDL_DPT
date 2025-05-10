import os.path
import pickle
import math
def load_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_all_data():
    vocab = load_pkl("vocab.pkl")
    metadata = load_pkl("metadata.pkl")
    tfidf_data = load_pkl("tf-idf.pkl")
    tfidf_dict = {doc["doc_id"]: doc["vector_sparse"] for doc in tfidf_data}
    tfidf_data = tfidf_dict
    inverted_index = load_pkl("inverted_index.pkl")
    if os.path.exists("norm2.pkl"):
        norm2 = load_pkl("norm2.pkl")
    else:
        norm2 = {}
        for doc_id in tfidf_data:  # chỉ tính cosine với những văn bản này
            doc_vector = tfidf_data[doc_id]
            norm = math.sqrt(sum(v ** 2 for v in doc_vector.values()))
            norm2[doc_id] = norm
        with open("norm2.pkl", "wb") as f:
            pickle.dump(norm2, f)
    idf = load_pkl("idf.pkl")
    return vocab, metadata, tfidf_data, inverted_index, norm2, idf
