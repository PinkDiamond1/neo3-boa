from typing import Any, Dict

from boa3.model.symbol import ISymbol
from boa3.model.type.itype import IType
from boa3.model.type.primitive.inttype import IntType


class FindOptionsType(IntType):
    """
    A class used to represent Neo interop FindOptions type
    """

    def __init__(self):
        super().__init__()
        self._identifier = 'FindOptions'

    @property
    def default_value(self) -> Any:
        from boa3.builtin.interop.storage import FindOptions
        return FindOptions.NONE

    @classmethod
    def build(cls, value: Any = None) -> IType:
        if cls._is_type_of(value) or value is None:
            from boa3.model.builtin.interop.interop import Interop
            return Interop.FindOptionsType

    @classmethod
    def _is_type_of(cls, value: Any):
        from boa3.builtin.interop.storage import FindOptions
        return isinstance(value, (FindOptions, FindOptionsType, type(int)))

    @property
    def symbols(self) -> Dict[str, ISymbol]:
        """
        Gets the class symbols of this type

        :return: a dictionary that maps each symbol in the module with its name
        """
        from boa3.builtin.interop.storage import FindOptions
        from boa3.model.variable import Variable

        return {name: Variable(self) for name in FindOptions.__members__.keys()}

    def get_value(self, symbol_id) -> Any:
        """
        Gets the literal value of a symbol

        :return: the value if this type has this symbol. None otherwise.
        """
        if symbol_id in self.symbols:
            from boa3.builtin.interop.storage import FindOptions
            return FindOptions.__members__[symbol_id]

        return None
