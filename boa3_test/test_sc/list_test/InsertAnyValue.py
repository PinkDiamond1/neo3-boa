from typing import Any, List

from boa3.builtin import public


@public
def Main(a: List[Any], pos: int, value: Any) -> List[Any]:
    a.insert(pos, value)
    return a
