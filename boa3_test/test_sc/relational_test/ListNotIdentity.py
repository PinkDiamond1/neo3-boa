from typing import List

from boa3.builtin import public


@public
def with_attribution() -> bool:
    a: List[int] = [1, 2, 3]
    b = a
    return a is not b


@public
def without_attribution() -> bool:
    a: List[int] = [1, 2, 3]
    b: List[int] = [1, 2, 3]
    return a is not b
