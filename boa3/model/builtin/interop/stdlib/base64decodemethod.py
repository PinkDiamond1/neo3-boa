from typing import Dict

from boa3.model.builtin.interop.nativecontract import StdLibMethod
from boa3.model.variable import Variable


class Base64DecodeMethod(StdLibMethod):

    def __init__(self):
        from boa3.model.type.type import Type
        identifier = 'base64_decode'
        native_identifier = 'base64Decode'
        args: Dict[str, Variable] = {'key': Variable(Type.str)}
        super().__init__(identifier, native_identifier, args, return_type=Type.bytes)