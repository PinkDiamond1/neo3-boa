from typing import List, Any

from boa3.model.type.itype import IType
from boa3.model.type.sequencetype import SequenceType
from boa3.neo.vm.type.AbiType import AbiType


class GenericSequenceType(SequenceType):
    """
    An class used to represent a generic Python sequence type
    """

    def __init__(self, values_type: List[IType]):
        identifier: str = 'sequence'
        values_type = self.filter_types(values_type)
        super().__init__(identifier, values_type)

    @property
    def abi_type(self) -> AbiType:
        return AbiType.Array  # TODO: change when 'bytes' is implemented

    def is_valid_key(self, value_type: IType) -> bool:
        return value_type == self.valid_key

    @property
    def valid_key(self) -> IType:
        from boa3.model.type.type import Type
        return Type.int

    @classmethod
    def build(cls, value: Any):
        if cls.is_type_of(value):
            values_types: List[IType] = cls.get_types(value)
            return cls(values_types)

    @classmethod
    def is_type_of(cls, value: Any):
        return isinstance(value, SequenceType)

    def __hash__(self):
        return hash(self.identifier + self.value_type.identifier)