from typing import Dict

from boa3.model.builtin.interop.nativecontract import ContractManagementMethod
from boa3.model.variable import Variable


class GetMinimumDeploymentFeeMethod(ContractManagementMethod):

    def __init__(self):
        from boa3.model.type.type import Type
        identifier = 'get_minimum_deployment_fee'
        syscall = 'getMinimumDeploymentFee'
        args: Dict[str, Variable] = {}
        super().__init__(identifier, syscall, args, return_type=Type.int)
