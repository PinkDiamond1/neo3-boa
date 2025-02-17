from typing import List, Optional, Tuple

from boa3.compiler.codegenerator import get_bytes_count
from boa3.model.builtin.method.maxmethod import MaxMethod
from boa3.model.type.itype import IType
from boa3.neo.vm.opcode.Opcode import Opcode


class MaxByteStringMethod(MaxMethod):

    def __init__(self, arg_value: Optional[IType] = None):
        from boa3.model.type.type import Type
        is_valid_type = Type.str.is_type_of(arg_value) or Type.bytes.is_type_of(arg_value)
        super().__init__(arg_value if is_valid_type else Type.str)

    def _compare_values(self) -> List[Tuple[Opcode, bytes]]:
        from boa3.neo.vm.type.Integer import Integer

        jmp_place_holder = (Opcode.JMP, b'\x01')

        test_if_are_equal = [
            (Opcode.OVER, b''),
            (Opcode.OVER, b''),
            (Opcode.EQUAL, b''),  # if str1 == str2:
            Opcode.get_jump_and_data(Opcode.JMPIFNOT, 4),
            (Opcode.PUSH1, b''),
            jmp_place_holder,     # go to final test
        ]

        get_limit_index = [
            (Opcode.OVER, b''),   # limit = min((len(str1), len(str2))
            (Opcode.SIZE, b''),
            (Opcode.OVER, b''),
            (Opcode.SIZE, b''),
            (Opcode.MIN, b''),
            (Opcode.PUSH0, b''),  # index = 0
        ]

        while_body_before_compare = [
            (Opcode.PUSH3, b''),  # value1 = str1[index]
            (Opcode.get_dup(3), b''),
            (Opcode.OVER, b''),
            (Opcode.PICKITEM, b''),
            (Opcode.OVER, b''),
            (Opcode.PUSH4, b''),  # value2 = str2[index]
            (Opcode.get_dup(4), b''),
            (Opcode.SWAP, b''),
            (Opcode.PICKITEM, b''),
        ]
        while_body_compare = [
            (Opcode.OVER, b''),
            (Opcode.OVER, b''),
            (Opcode.JMPEQ, Integer(7).to_byte_array(signed=True)),     # if value1 != value2 jmp to end
            (Opcode.GT, b''),
            (Opcode.NIP, b''),
            (Opcode.NIP, b''),
            jmp_place_holder,     # jmp to end
        ]
        while_body_after_compare = [
            (Opcode.DROP, b''),
            (Opcode.DROP, b''),
            (Opcode.INC, b''),    # index++
        ]

        while_full_body = while_body_before_compare + while_body_compare + while_body_after_compare
        while_bytes_size = get_bytes_count(while_full_body)
        get_limit_index.append(
            Opcode.get_jump_and_data(Opcode.JMP, while_bytes_size, True)
        )

        while_condition = [
            (Opcode.OVER, b''),
            (Opcode.OVER, b'')
        ]
        while_condition_bytes_size = get_bytes_count(while_condition)
        while_condition.append(Opcode.get_jump_and_data(Opcode.JMPGT, -while_bytes_size - while_condition_bytes_size))

        while_else_body = [
            (Opcode.DROP, b''),
            (Opcode.DROP, b''),
            (Opcode.OVER, b''),  # if len(str1) > len(str2) jmp to end
            (Opcode.SIZE, b''),
            (Opcode.OVER, b''),
            (Opcode.SIZE, b''),
            (Opcode.GT, b''),
        ]

        everything_after_while_check = while_body_after_compare + while_condition + while_else_body
        jmp_while_check = Opcode.get_jump_and_data(Opcode.JMP, get_bytes_count(everything_after_while_check), True)
        while_body_compare[-1] = jmp_while_check

        everything_after_equal_check = (get_limit_index +
                                        while_body_before_compare +
                                        while_body_compare +
                                        everything_after_while_check)
        jmp_test_equal = Opcode.get_jump_and_data(Opcode.JMP, get_bytes_count(everything_after_equal_check), True)
        test_if_are_equal[-1] = jmp_test_equal

        final_test = [
            (Opcode.JMPIFNOT, Integer(4).to_byte_array(signed=True)),   # if condition is True
            (Opcode.DROP, b''),                                            # remove str2 <=> return str1
            (Opcode.JMP, Integer(3).to_byte_array(signed=True)),        # else
            (Opcode.NIP, b'')                                              # remove str1 <=> return str2
        ]

        return (
            test_if_are_equal +
            everything_after_equal_check +
            final_test
        )
