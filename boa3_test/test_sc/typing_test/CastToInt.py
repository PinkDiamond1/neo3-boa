from typing import Any, cast

from boa3.builtin import public


@public
def Main(value: Any) -> int:
    x = cast(int, value)
    return x
