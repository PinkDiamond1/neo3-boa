from boa3.builtin import public


class Example:
    val1 = 1
    val2 = 2

    @classmethod
    def foo(cls) -> int:
        return cls.val1


@public
def get_val1() -> int:
    return Example().val1


@public
def get_val2() -> int:
    return Example().val2
