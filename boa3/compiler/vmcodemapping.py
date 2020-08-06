from typing import Dict, List

from boa3.neo.vm.VMCode import VMCode
from boa3.neo.vm.opcode.OpcodeInformation import OpcodeInformation


class VMCodeMapping:
    """
    This class is responsible for managing the Neo VM instruction during the bytecode generation.
    """
    _instance = None  # type:VMCodeMapping

    @classmethod
    def instance(cls):
        """
        :return: the singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._codes: Dict[int, VMCode] = {}

    @classmethod
    def reset(cls):
        """
        Resets the map to the first state
        """
        if cls._instance is not None:
            cls._instance._codes.clear()

    @property
    def codes(self) -> List[VMCode]:
        """
        Gets a list with the included vm codes

        :return: a list of vm codes ordered by its address in the bytecode
        """
        return list(self.code_map.values())

    @property
    def code_map(self) -> Dict[int, VMCode]:
        """
        Gets a dictionary that maps each vm code with its address.

        :return: a dictionary that maps each instruction with its address. The keys are ordered by the address.
        """
        return {key: self._codes[key] for key in sorted(self._codes)}

    def bytecode(self) -> bytes:
        """
        Gets the bytecode of the translated code

        :return: the generated bytecode
        """
        self._update_larger_codes()

        bytecode = bytearray()
        for code in self.codes:
            bytecode += code.opcode
            if code.data is not None:
                bytecode += code.data
        return bytes(bytecode)

    @property
    def bytecode_size(self) -> int:
        if len(self._codes) < 1:
            return 0

        last_key = list(self.code_map)[-1]
        return last_key + self._codes[last_key].size

    def insert_code(self, vm_code: VMCode):
        if vm_code not in self._codes.values():
            self._codes[self.bytecode_size] = vm_code

    def get_start_address(self, vm_code: VMCode) -> int:
        """
        Gets the vm code's first byte address

        :param vm_code: the instruction to get the address
        :return: the vm code's address if it's in the map. Otherwise, return's zero.
        """
        if vm_code not in self._codes.values():
            return 0
        return next(key for key, value in self._codes.items() if value == vm_code)

    def get_end_address(self, vm_code: VMCode) -> int:
        """
        Gets the vm code's last byte address

        :param vm_code: the instruction to get the address
        :return: the vm code's last address if it's in the map. Otherwise, return's zero.
        """
        if vm_code not in self._codes.values():
            return 0
        return self.get_start_address(vm_code) + vm_code.size - 1  # start + size returns next opcode address

    def update_vm_code(self, vm_code: VMCode, opcode: OpcodeInformation, data: bytes = bytes()):
        """
        Updates the information from an inserted code

        :param vm_code: code to be updated
        :param opcode: updated opcode information
        :param data: updated opcode data
        """
        code_size = vm_code.size
        vm_code._info = opcode
        vm_code._data = data
        if vm_code.size != code_size:
            self._update_addresses(self.get_start_address(vm_code))

    def _update_addresses(self, start_address: int = 0):
        """
        Updates the instruction map's keys when a opcode is changed

        :param start_address: the address from the changed opcode
        """
        new_address = -1
        last_code: VMCode = None
        updated_codes: Dict[int, VMCode] = {}

        for address, code in list(self.code_map.items()):
            if address >= start_address:
                if new_address < 0:
                    new_address = self.get_start_address(last_code) if last_code is not None else 0

                new_address += last_code.size
                if new_address != address:
                    updated_codes[new_address] = self._codes.pop(address)
            last_code = code
        self._codes.update(updated_codes)

    def move_to_end(self, first_code_address: int, last_code_address: int):
        """
        Moves a set of instructions to the end of the current bytecode

        :param first_code_address: first instruction start address
        :param last_code_address: last instruction end address
        """
        if last_code_address < first_code_address:
            return

        moved_codes: List[VMCode] = []
        for address in list(self.code_map):
            if first_code_address <= address <= last_code_address:
                moved_codes.append(self._codes.pop(address))
            elif address > last_code_address:
                break

        self._update_addresses(first_code_address)

        for code in moved_codes:
            self.insert_code(code)
        self._update_targets()

    def _update_targets(self):
        from boa3.neo.vm.type.Integer import Integer
        for address, code in self.code_map.items():
            if code.opcode.has_target() and code.target is None:
                relative = Integer.from_bytes(code.data)
                absolute = address + relative
                if absolute in self.code_map:
                    code.set_target = self.code_map[absolute]

    def _update_larger_codes(self):
        """
        Checks if each instruction data fits in its opcode maximum size and updates the opcode from those that don't
        """
        # gets a list with all instructions which its opcode has a larger equivalent, ordered by its address
        instr_with_small_codes = [code for code in self._codes.values() if code.opcode.has_larger_opcode()]
        instr_with_small_codes.sort(key=lambda code: self.get_start_address(code), reverse=True)

        from boa3.neo.vm.opcode.OpcodeInfo import OpcodeInfo
        # total_len is initialized with zero because the loop must run at least once
        total_len = 0
        current_size = self.bytecode_size

        # if any instruction is updated, the following instruction addresses and the total size will change as well
        # with the change, previous instruction data may have overflowed the opcode maximum value
        # to make sure, it must check the opcodes that haven't changed again
        while total_len != current_size:
            total_len = current_size

            # verifies each instruction data length
            for code in instr_with_small_codes.copy():  # it's a copy because the list may change during the iteration
                if len(code.raw_data) > code.info.max_data_len:
                    # gets the shortest opcode equivalent that fits the instruction data
                    info = OpcodeInfo.get_info(code.opcode.get_larger_opcode())
                    while len(code.raw_data) > info.max_data_len and info.opcode.has_larger_opcode():
                        info = OpcodeInfo.get_info(code.opcode.get_larger_opcode())

                    self.update_vm_code(code, info)
                    if info.opcode == info.opcode.get_larger_opcode():
                        # if it's the largest equivalent, it won't be updated anymore
                        instr_with_small_codes.remove(code)
            current_size = self.bytecode_size