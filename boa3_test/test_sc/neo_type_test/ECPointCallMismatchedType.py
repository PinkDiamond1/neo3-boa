from boa3.builtin import public
from boa3.builtin.type import ECPoint


@public
def ecpoint(arg: str) -> ECPoint:
    return ECPoint(arg)
