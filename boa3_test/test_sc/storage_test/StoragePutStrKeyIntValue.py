from boa3.builtin import NeoMetadata, metadata
from boa3.builtin.interop.storage import put


def Main(key: str):
    value: int = 123
    put(key, value)


@metadata
def manifest() -> NeoMetadata:
    meta = NeoMetadata()
    meta.has_storage = True
    return meta
