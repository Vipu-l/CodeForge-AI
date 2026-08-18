import os
import pickle


INDEX_DIRECTORY = "indexes"

_indexes = {}


def _get_index_path(repository_name: str) -> str:
    """
    Return the disk path for a repository index.
    """

    os.makedirs(
        INDEX_DIRECTORY,
        exist_ok=True
    )

    return os.path.join(
        INDEX_DIRECTORY,
        f"{repository_name}.pkl"
    )


def save_index(
    repository_name: str,
    index
):
    """
    Save the latest repository index.

    The index is stored:
    1. In memory for fast access.
    2. On disk so it survives server restarts.
    """

    _indexes[repository_name] = index

    index_path = _get_index_path(
        repository_name
    )

    temporary_path = index_path + ".tmp"

    try:

        with open(
            temporary_path,
            "wb"
        ) as file:

            pickle.dump(
                index,
                file,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        # Replace the previous index only after
        # the new index has been written successfully.
        os.replace(
            temporary_path,
            index_path
        )

    except Exception:

        # Remove incomplete temporary file.
        if os.path.exists(
            temporary_path
        ):
            try:
                os.remove(
                    temporary_path
                )
            except OSError:
                pass

        raise


def load_index(
    repository_name: str
):
    """
    Load a repository index from disk.

    The loaded index is cached in memory.
    """

    if repository_name in _indexes:

        return _indexes[
            repository_name
        ]

    index_path = _get_index_path(
        repository_name
    )

    if not os.path.isfile(
        index_path
    ):
        return None

    try:

        with open(
            index_path,
            "rb"
        ) as file:

            index = pickle.load(
                file
            )

        _indexes[
            repository_name
        ] = index

        return index

    except (
        OSError,
        pickle.PickleError,
        EOFError,
        AttributeError,
        ImportError,
        ModuleNotFoundError
    ):

        return None


def get_index(
    repository_name: str
):
    """
    Return the currently loaded repository index.

    If it is not already in memory,
    load it from disk.
    """

    if repository_name in _indexes:

        return _indexes[
            repository_name
        ]

    return load_index(
        repository_name
    )


def remove_index(
    repository_name: str
):
    """
    Remove a repository index from memory
    and delete its persisted copy.
    """

    _indexes.pop(
        repository_name,
        None
    )

    index_path = _get_index_path(
        repository_name
    )

    if os.path.isfile(
        index_path
    ):

        try:

            os.remove(
                index_path
            )

        except OSError:
            pass


def clear_memory_cache():
    """
    Clear all indexes currently cached in memory.

    Disk indexes are not deleted.
    """

    _indexes.clear()