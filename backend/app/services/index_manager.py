_indexes = {}


def save_index(repository_name: str, index):
    _indexes[repository_name] = index


def get_index(repository_name: str):
    return _indexes.get(repository_name)


def remove_index(repository_name: str):
    _indexes.pop(repository_name, None)