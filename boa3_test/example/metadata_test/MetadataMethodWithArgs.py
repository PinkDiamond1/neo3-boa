from boa3.builtin import metadata, NeoMetadata


def Main() -> int:
    return 5


@metadata
def example(arg0: int, arg1: str) -> NeoMetadata:
    # this function doesn't allow arguments
    return NeoMetadata()

