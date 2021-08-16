from typing import List

from boa3.model.builtin.interop.blockchain import BlockType, TransactionType
from boa3.model.builtin.native import *
from boa3.model.identifiedsymbol import IdentifiedSymbol
from boa3.model.imports.package import Package


class NativeContract:

    # Interop Types
    BlockType = BlockType.build()
    TransactionType = TransactionType.build()

    # Class Interfaces
    Ledger = LedgerClass()
    Policy = PolicyClass()

    # region Packages

    LedgerModule = Package(identifier=Ledger.identifier.lower(),
                           types=[Ledger,
                                  BlockType,
                                  TransactionType]
                           )

    PolicyModule = Package(identifier=Policy.identifier.lower(),
                           types=[Policy]
                           )

    # endregion

    package_symbols: List[IdentifiedSymbol] = [
        LedgerModule,
        PolicyModule
    ]
