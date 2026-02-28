from .hash_index import HashIndex
from .range_index import RangeIndex


class IndexFactory:
    _registry = {
        "hash": HashIndex,
        "range": RangeIndex
    }

    @classmethod
    def create(cls, index_type: str):
        return cls._registry[index_type]()