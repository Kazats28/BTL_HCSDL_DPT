import pickle

def save_pkl(PATH, TEXT):
    with open(PATH + ".pkl", "wb") as f:
        pickle.dump(TEXT, f)