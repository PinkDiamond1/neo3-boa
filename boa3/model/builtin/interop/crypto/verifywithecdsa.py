from typing import Dict

from boa3.model.builtin.interop.nativecontract import CryptoLibMethod
from boa3.model.variable import Variable


class VerifyWithECDsaMethod(CryptoLibMethod):

    def __init__(self):
        from boa3.model.type.type import Type
        from boa3.model.type.collection.sequence.ecpointtype import ECPointType
        from boa3.model.builtin.interop.crypto.namedcurvetype import NamedCurveType

        identifier = 'verify_with_ecdsa'
        native_identifier = 'verifyWithECDsa'
        args: Dict[str, Variable] = {
            'data': Variable(Type.any),
            'pubkey': Variable(ECPointType.build()),
            'signature': Variable(Type.union.build([Type.str,
                                                    Type.bytes])),
            'curve': Variable(NamedCurveType.build())
        }
        super().__init__(identifier, native_identifier, args, return_type=Type.bool)
