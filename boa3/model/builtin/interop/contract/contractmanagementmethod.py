import ast
from typing import Dict, List, Tuple

from boa3.model.builtin.interop.interopmethod import InteropMethod
from boa3.model.type.itype import IType
from boa3.model.variable import Variable
from boa3.neo.vm.opcode.Opcode import Opcode


class ContractManagementMethod(InteropMethod):

    def __init__(self, identifier: str, syscall: str, args: Dict[str, Variable] = None,
                 defaults: List[ast.AST] = None, return_type: IType = None):
        super().__init__(identifier, syscall, args, defaults, return_type)

    @property
    def opcode(self) -> List[Tuple[Opcode, bytes]]:
        from boa3.model.builtin.interop.interop import Interop
        from boa3.neo.vm.type.Integer import Integer
        from boa3.neo.vm.type.String import String

        method = String(self._sys_call).to_bytes()
        opcode = [
            (Opcode.PUSHDATA1, Integer(len(method)).to_byte_array(min_length=1) + method)
        ]
        return (opcode
                + Interop.ManagementContractScriptHash.getter.opcode
                + Interop.CallContract.opcode
                )

    @property
    def pack_arguments(self) -> bool:
        return True

    @property
    def method_name(self) -> str:
        return self._sys_call