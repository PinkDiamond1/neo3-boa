import sys
from typing import Dict, Any

from boa3.analyser.analyser import Analyser
from boa3.constants import ONE_BYTE_MAX_VALUE, TWO_BYTES_MAX_VALUE
from boa3.model.method import Method
from boa3.model.symbol import ISymbol
from boa3.model.type.type import Type
from boa3.neo.vm.VMCode import VMCode
from boa3.neo.vm.Opcode import Opcode
from boa3.neo.vm.type.Integer import Integer
from boa3.neo.vm.type.StackItemType import StackItemType


class CodeGenerator:
    """
    This class is responsible for generating the Neo VM bytecode

    :ivar symbol_table: a dictionary that maps the global symbols.
    """

    @staticmethod
    def generate_code(analyser: Analyser) -> bytes:
        """
        Generates the Neo VM bytecode using of the analysed Python code

        :param analyser: semantic analyser it tge Python code
        :return: the Neo VM bytecode
        """
        from boa3.compiler.codegeneratorvisitor import VisitorCodeGenerator

        generator = CodeGenerator(analyser.symbol_table)
        visitor = VisitorCodeGenerator(generator)
        visitor.visit(analyser.ast_tree)
        return generator.bytecode

    def __init__(self, symbol_table: Dict[str, ISymbol]):
        self.symbol_table: Dict[str, ISymbol] = symbol_table
        self.__address: int = 0
        self.__vm_codes: Dict[int, VMCode] = {}

    @property
    def bytecode(self) -> bytes:
        """
        Gets the bytecode of the translated code

        :return: the generated bytecode
        """
        bytecode = bytearray()
        for code in self.__vm_codes.values():
            bytecode += code.opcode.value
            if code.data is not None:
                bytecode += code.data
        return bytes(bytecode)

    def get_symbol(self, identifier: str) -> ISymbol:
        """
        Gets a symbol in the symbol table by its id

        :param identifier: id of the symbol
        :return: the symbol if exists. Symbol None otherwise
        """
        if identifier in self.symbol_table:
            return self.symbol_table[identifier]
        return Type.none.symbol

    def convert_begin_method(self, method: Method):
        """
        Converts the signature of the method

        :param method: method that is being converted
        """
        num_args: int = len(method.args)
        num_vars: int = len(method.locals)

        init_data = bytearray([num_vars, num_args])
        self.__insert1(Opcode.INITSLOT, init_data)

    def convert_end_method(self):
        """
        Converts the end of the method
        """
        self.__insert1(Opcode.RET)

    def convert_literal(self, value: Any):
        """
        Converts a literal value

        :param value: the value to be converted
        """
        if isinstance(value, int):
            self.convert_integer_literal(value)
        elif isinstance(value, str):
            self.convert_string_literal(value)
        elif isinstance(value, bool):
            self.convert_bool_literal(value)
        else:
            # TODO: convert other python literals as they are implemented
            pass

    def convert_integer_literal(self, value: int):
        """
        Converts an integer literal value

        :param value: the value to be converted
        """
        if -1 <= value <= 16:
            opcode = Opcode.get_literal_push(value)
            if opcode is not None:
                self.__insert1(opcode)
        else:
            array = Integer(value).to_byte_array()
            self.convert_byte_array(array)
            # cast the value to integer
            self.__insert1(Opcode.CONVERT, StackItemType.Integer.value)
        pass

    def convert_string_literal(self, value: str):
        """
        Converts an string literal value

        :param value: the value to be converted
        """
        array = bytes(value, sys.getdefaultencoding())
        self.convert_byte_array(array)

    def convert_bool_literal(self, value: bool):
        """
        Converts an boolean literal value

        :param value: the value to be converted
        """
        if value:
            self.__insert1(Opcode.PUSH1)
        else:
            self.__insert1(Opcode.PUSH0)

    def convert_byte_array(self, array: bytes):
        """
        Converts a byte value

        :param array: the value to be converted
        """
        data_len: int = len(array)
        if data_len <= ONE_BYTE_MAX_VALUE:
            prefix_len = 1
            code = Opcode.PUSHDATA1
        elif data_len <= TWO_BYTES_MAX_VALUE:
            prefix_len = 2
            code = Opcode.PUSHDATA2
        else:
            prefix_len = 4
            code = Opcode.PUSHDATA4

        data = data_len.to_bytes(prefix_len, sys.byteorder) + array
        self.__insert1(code, data)

    def __insert1(self, opcode: Opcode, data: bytes = None):
        """
        Inserts one opcode into the bytecode

        :param opcode: opcode that will be inserted
        :param data: data of the opcode, if needed
        """
        start_address = self.__address
        vm_code = VMCode(opcode, start_address, data)

        self.__vm_codes[start_address] = vm_code
        self.__address += 1

        if data is not None:
            self.__address += len(data)
