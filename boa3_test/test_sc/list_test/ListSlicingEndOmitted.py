from boa3.builtin import public


@public
def Main() -> list:
    a = [0, 1, 2, 3, 4, 5]
    return a[2:]   # expect [2, 3, 4, 5]
