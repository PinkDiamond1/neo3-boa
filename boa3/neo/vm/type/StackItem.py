from __future__ import annotations

from enum import Enum
from typing import Any

from boa3.neo.vm.type.Integer import Integer
from boa3.neo.vm.type.String import String


class StackItemType(bytes, Enum):
    Any = b'\x00'
    Pointer = b'\x10'
    Boolean = b'\x20'
    Integer = b'\x21'
    ByteString = b'\x28'
    Buffer = b'\x30'
    Array = b'\x40'
    Struct = b'\x41'
    Map = b'\x48'
    InteropInterface = b'\x60'

    @classmethod
    def get_stack_item_type(cls, stack_item_type: str) -> StackItemType:
        try:
            return StackItemType[stack_item_type]
        except BaseException:
            return StackItemType.Any


def serialize(value: Any) -> bytes:
    if value is None:
        return StackItemType.Any

    if isinstance(value, (int, str, bytes)):
        if isinstance(value, int):
            stack_type = StackItemType.Integer
            span = Integer(value).to_byte_array(signed=True, min_length=1)
        elif isinstance(value, str):
            stack_type = StackItemType.ByteString
            span = String(value).to_bytes()
        else:
            stack_type = StackItemType.Buffer
            span = value

        return (stack_type
                + Integer(len(span)).to_byte_array(signed=False, min_length=1)
                + span)

    if isinstance(value, (list, tuple, set, range)):
        serialized = StackItemType.Array + Integer(len(value)).to_byte_array(signed=False)
        for x in value:
            serialized += serialize(x)
        return serialized

    if isinstance(value, dict):
        serialized = StackItemType.Map + Integer(len(value)).to_byte_array(signed=False)
        for key, x in value.items():
            serialized += serialize(key)
            serialized += serialize(x)
        return serialized

    return b''
