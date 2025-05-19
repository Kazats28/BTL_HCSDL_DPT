import pickle

def load_pkl(PATH):
    with open(PATH + ".pkl", "rb") as f:
        data = pickle.load(f)
        return data