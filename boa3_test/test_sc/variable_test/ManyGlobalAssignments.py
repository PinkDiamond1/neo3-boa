from typing import List

from boa3.builtin import public

a = 0
b = 1
c = 2
d = 3
e = 4
f = 5
g = 6
h = 7


@public
def Main() -> List[int]:
    return [a, b, c, d, e, f, g, h]
