from typing import Any

from boa3.model.type.collection.sequence.sequencetype import SequenceType
from boa3.model.type.itype import IType


class ReversedType(SequenceType):
    """
    A class used to represent Python reversed type. It's represented as a Sequence instead of a Iterable.
    """

    def __init__(self, values_type: IType = None):
        identifier = 'reversed'
        values_type = self.filter_types(values_type)
        super().__init__(identifier, values_type)

    @property
    def default_value(self) -> Any:
        return reversed([])

    @property
    def identifier(self) -> str:
        return self._identifier

    @classmethod
    def build(cls, value: Any) -> IType:
        if cls._is_type_of(value):
            from boa3.model.type.type import Type
            return cls(Type.reversed)

    def is_valid_key(self, key_type: IType) -> bool:
        return key_type == self.valid_key

    @property
    def valid_key(self) -> IType:
        from boa3.model.type.type import Type
        return Type.int

    @classmethod
    def _is_type_of(cls, value: Any):
        return type(value) is reversed or isinstance(value, ReversedType)

    @property
    def can_reassign_values(self) -> bool:
        return False

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.value_type == other.value_type

    def __hash__(self):
        return hash(self.identifier)