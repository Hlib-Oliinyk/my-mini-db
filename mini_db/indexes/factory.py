from .hash_index import HashIndex


class IndexFactory:
    _registry = {
        "hash": HashIndex
    }

    @classmethod
    def create(cls, index_type: str):
        return cls._registry[index_type]()