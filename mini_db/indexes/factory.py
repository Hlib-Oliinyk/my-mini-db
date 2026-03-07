from .hash_index import HashIndex
from .range_index import RangeIndex
from .composite_index import CompositeIndex


class IndexFactory:
    _registry = {
        "hash": HashIndex,
        "range": RangeIndex,
        "composite": CompositeIndex
    }

    @classmethod
    def create(cls, index_type: str):
        return cls._registry[index_type]()