from __future__ import annotations

from typing import Any, Dict, Optional

from boa3.model.method import Method
from boa3.model.property import Property
from boa3.model.type.classes.classstructtype import ClassStructType
from boa3.model.variable import Variable


class ContractPermissionDescriptorType(ClassStructType):
    """
    A class used to represent Neo ContractPermissionDescriptor class
    """

    def __init__(self):
        super().__init__('ContractPermissionDescriptor')
        from boa3.model.type.collection.sequence.uint160type import UInt160Type
        from boa3.model.type.collection.sequence.ecpointtype import ECPointType
        from boa3.model.type.type import Type

        self._variables: Dict[str, Variable] = {
            'hash': Variable(Type.optional.build(UInt160Type.build())),
            'group': Variable(Type.optional.build(ECPointType.build()))
        }
        self._constructor: Method = None

    @property
    def variables(self) -> Dict[str, Variable]:
        return self._variables.copy()

    @property
    def properties(self) -> Dict[str, Property]:
        return {}

    @property
    def class_methods(self) -> Dict[str, Method]:
        return {}

    @property
    def instance_methods(self) -> Dict[str, Method]:
        return {}

    def constructor_method(self) -> Optional[Method]:
        return self._constructor

    @classmethod
    def build(cls, value: Any = None) -> ContractPermissionDescriptorType:
        if value is None or cls._is_type_of(value):
            return _ContractPermissionDescriptor

    @classmethod
    def _is_type_of(cls, value: Any):
        return isinstance(value, ContractPermissionDescriptorType)


_ContractPermissionDescriptor = ContractPermissionDescriptorType()