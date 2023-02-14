import pickle

def persist_model(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def load_model(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)