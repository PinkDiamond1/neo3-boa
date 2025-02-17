from typing import Any

from boa3.builtin import public
from boa3.builtin.interop.blockchain import Transaction


@public
def get_transaction_hash(value: Any) -> bytes:
    tx: Transaction = value
    return tx.hash
