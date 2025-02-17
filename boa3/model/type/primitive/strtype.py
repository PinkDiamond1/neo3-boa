from typing import Any

from boa3.model.type.itype import IType
from boa3.model.type.primitive.bytestringtype import ByteStringType
from boa3.neo.vm.type.AbiType import AbiType


class StrType(ByteStringType):
    """
    A class used to represent Python str type
    """

    def __init__(self):
        identifier = 'str'
        super().__init__(identifier, [self])

    @property
    def default_value(self) -> Any:
        return str()

    @property
    def abi_type(self) -> AbiType:
        return AbiType.String

    def _init_class_symbols(self):
        super()._init_class_symbols()

        from boa3.model.builtin.builtin import Builtin

        instance_methods = [Builtin.StrSplit,
                            Builtin.ConvertToBytes
                            ]

        for instance_method in instance_methods:
            self._instance_methods[instance_method.raw_identifier] = instance_method.build(self)

    @classmethod
    def build(cls, value: Any) -> IType:
        if cls._is_type_of(value):
            from boa3.model.type.type import Type
            return Type.str

    @classmethod
    def build_collection(cls, value_type: IType):
        from boa3.model.type.type import Type
        return Type.str

    @classmethod
    def _is_type_of(cls, value: Any) -> bool:
        return type(value) in [str, StrType]

    def is_type_of(self, value: Any) -> bool:
        return self._is_type_of(value)
