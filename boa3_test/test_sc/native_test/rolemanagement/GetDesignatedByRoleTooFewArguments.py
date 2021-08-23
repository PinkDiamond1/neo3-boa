from boa3.builtin.interop.role import Role
from boa3.builtin.nativecontract.rolemanagement import RoleManagement
from boa3.builtin.type import ECPoint


def main(role: Role) -> ECPoint:
    return RoleManagement.get_designated_by_role(role)
