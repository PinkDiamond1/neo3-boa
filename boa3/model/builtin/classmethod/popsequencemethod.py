import ast
from typing import Dict, Optional

from boa3.model.builtin.classmethod.popmethod import PopMethod
from boa3.model.type.itype import IType
from boa3.model.variable import Variable


class PopSequenceMethod(PopMethod):

    def __init__(self, arg_value: Optional[IType] = None):
        from boa3.model.type.type import Type

        if not Type.mutableSequence.is_type_of(arg_value):
            arg_value = Type.mutableSequence

        args: Dict[str, Variable] = {
            'self': Variable(arg_value),
            'index': Variable(arg_value.valid_key)
        }

        index_default = ast.parse("-1").body[0].value.operand
        index_default.n = -1

        super().__init__(args, defaults=[index_default], return_type=arg_value.value_type)
