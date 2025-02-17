import ast
from typing import Any, Dict, List, Optional, Tuple, Union

from boa3.model.builtin.method.builtinmethod import IBuiltinMethod
from boa3.model.type.primitive.bytestype import BytesType
from boa3.model.type.primitive.strtype import StrType
from boa3.model.variable import Variable
from boa3.neo.vm.opcode.Opcode import Opcode


class StartsWithMethod(IBuiltinMethod):
    def __init__(self, self_type: Union[StrType, BytesType] = None):
        from boa3.model.type.type import Type

        if not isinstance(self_type, (StrType, BytesType)):
            self_type = Type.str

        identifier = 'startswith'
        args: Dict[str, Variable] = {
            'self': Variable(self_type),
            'value': Variable(self_type),
            'start': Variable(Type.int),
            'end': Variable(Type.int),
        }

        start_default = ast.parse("{0}".format(0)
                                  ).body[0].value
        end_default = ast.parse("-1").body[0].value.operand
        end_default.n = -1

        super().__init__(identifier, args, defaults=[start_default, end_default], return_type=Type.bool)

    @property
    def _arg_self(self) -> Variable:
        return self.args['self']

    @property
    def opcode(self) -> List[Tuple[Opcode, bytes]]:
        from boa3.compiler.codegenerator import get_bytes_count
        from boa3.neo.vm.type.StackItem import StackItemType

        jmp_place_holder = (Opcode.JMP, b'\x01')
        # string, end, start, substring

        verify_negative_index = [           # verify if index is negative value
            (Opcode.DUP, b''),
            (Opcode.PUSHM1, b''),
            jmp_place_holder                # if not index < 0, jump to verify_big_end
        ]

        fix_negative_end = [                # fix negative value to a positive equivalent
            (Opcode.PUSH3, b''),
            (Opcode.PICK, b''),
            (Opcode.SIZE, b''),
            (Opcode.ADD, b''),
            (Opcode.INC, b''),              # end = end + len(string) + 1
            (Opcode.DUP, b''),
            (Opcode.PUSHM1, b''),
            jmp_place_holder                # if not end < 0, jump to verify_and_fix_start
        ]

        fix_still_negative_index = [        # if end still is less than 0, then it should be 0
            (Opcode.DROP, b''),
            (Opcode.PUSH0, b''),            # end = 0
        ]

        jmp_fix_negative_index = Opcode.get_jump_and_data(Opcode.JMPGT, get_bytes_count(fix_negative_end +
                                                                                        fix_still_negative_index), True)
        verify_negative_index[-1] = jmp_fix_negative_index

        verify_big_end = [                  # verify if end is greater or equals to len(string)
            (Opcode.DUP, b''),
            (Opcode.PUSH4, b''),
            (Opcode.PICK, b''),
            (Opcode.SIZE, b''),
            jmp_place_holder                # if not end >= len(string), jump to verify_and_fix_start
        ]

        fix_big_end = [                     # fix end value to a positive equivalent
            (Opcode.DROP, b''),
            (Opcode.PUSH2, b''),
            (Opcode.PICK, b''),
            (Opcode.SIZE, b''),             # end = len(string)
        ]

        jmp_other_verifies = Opcode.get_jump_and_data(Opcode.JMPGT, get_bytes_count(fix_still_negative_index +
                                                                                    verify_big_end +
                                                                                    fix_big_end), True)
        fix_negative_end[-1] = jmp_other_verifies

        jmp_fix_big_index = Opcode.get_jump_and_data(Opcode.JMPLE, get_bytes_count(fix_big_end), True)
        verify_big_end[-1] = jmp_fix_big_index

        verify_and_fix_end = [              # verify and fix end index
            (Opcode.REVERSE3, b''),         # change positions on stack
        ]
        verify_and_fix_end.extend(verify_negative_index)
        verify_and_fix_end.extend(fix_negative_end)
        verify_and_fix_end.extend(fix_still_negative_index)
        verify_and_fix_end.extend(verify_big_end)
        verify_and_fix_end.extend(fix_big_end)

        verify_and_fix_start = [            # verify and fix end index
            (Opcode.SWAP, b''),             # change positions on stack
        ]

        # fix_negative_start is the same as fix_negative_end, but jump is different
        fix_negative_start = fix_negative_end.copy()
        verify_big_start = [                # verify if start is greater or equals to len(string)
            (Opcode.DUP, b''),
            (Opcode.PUSH4, b''),
            (Opcode.PICK, b''),
            (Opcode.SIZE, b''),
            jmp_place_holder                # if start >= len(string), return False
        ]

        jmp_other_verifies = Opcode.get_jump_and_data(Opcode.JMPGT, get_bytes_count(fix_still_negative_index +
                                                                                    verify_big_start), True)
        fix_negative_end[-1] = jmp_other_verifies

        verify_size = [                     # verify if len(string[start:end]) > len(substring)
            (Opcode.REVERSE3, b''),
            (Opcode.REVERSE4, b''),
            (Opcode.REVERSE3, b''),
            (Opcode.OVER, b''),
            (Opcode.SUB, b''),
            (Opcode.SUBSTR, b''),

            (Opcode.PUSH0, b''),
            (Opcode.PUSH2, b''),
            (Opcode.PICK, b''),
            (Opcode.SIZE, b''),
            (Opcode.DUP, b''),
            (Opcode.PUSH3, b''),
            (Opcode.PICK, b''),
            (Opcode.SIZE, b''),
            jmp_place_holder                # if len(string[start:end]) > len(substring), return False
        ]

        compare_starts = [                  # string.startswith(substring)
            (Opcode.SUBSTR, b''),
            (Opcode.CONVERT, StackItemType.ByteString),
            (Opcode.NUMEQUAL, b''),         # return string[start:end][0:len(substring)] == substring
            jmp_place_holder                # jumps other opcodes
        ]

        jmp_compare_starts = Opcode.get_jump_and_data(Opcode.JMPGT, get_bytes_count(compare_starts), True)
        verify_size[-1] = jmp_compare_starts

        jmp_to_false = Opcode.get_jump_and_data(Opcode.JMPGE, get_bytes_count(verify_size +
                                                                              compare_starts), True)
        verify_big_start[-1] = jmp_to_false

        verify_and_fix_start.extend(verify_negative_index)
        verify_and_fix_start.extend(fix_negative_start)
        verify_and_fix_start.extend(fix_still_negative_index)
        verify_and_fix_start.extend(verify_big_start)

        return_false = [                    # remove all values from stack and put False
            (Opcode.DROP, b''),
            (Opcode.DROP, b''),
            (Opcode.DROP, b''),
            (Opcode.DROP, b''),
            (Opcode.PUSH0, b''),            # return False
        ]

        jmp_bigger_substr = Opcode.get_jump_and_data(Opcode.JMP, get_bytes_count(return_false), True)
        compare_starts[-1] = jmp_bigger_substr

        return (
            verify_and_fix_end +
            verify_and_fix_start +
            verify_size +
            compare_starts +
            return_false
        )

    def push_self_first(self) -> bool:
        return self.has_self_argument

    @property
    def _args_on_stack(self) -> int:
        return len(self.args)

    @property
    def _body(self) -> Optional[str]:
        return None

    def build(self, value: Any) -> IBuiltinMethod:
        if isinstance(value, (StrType, BytesType)):
            return StartsWithMethod(value)
        return super().build(value)
