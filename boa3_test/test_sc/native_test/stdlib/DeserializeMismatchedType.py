from typing import Any

from boa3.builtin import public
from boa3.builtin.nativecontract.stdlib import StdLib


@public
def deserialize_arg() -> Any:
    return StdLib.deserialize(1)
