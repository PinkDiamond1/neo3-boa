from typing import Tuple


def Main() -> int:
    a: int = 0
    sequence: Tuple[int] = (3, 5, 15)

    for x in sequence:
        a = a + x

    return a