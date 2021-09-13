from boa3.builtin.nativecontract.gas import GAS
from boa3.builtin.type import UInt160


def main(from_address: UInt160, to_address: UInt160) -> bool:
    return GAS.transfer(from_address, to_address)
