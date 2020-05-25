from abc import ABC
from typing import Union, Iterable


class CompilerError(ABC, Exception):
    """
    An interface for compilation errors
    """
    def __init__(self, line: int, col: int, message: str = None):
        self.line: int = line
        self.col: int = col

        self.message = "%s:%s" % (line, col)
        if message is not None:
            self.message += " - %s" % message

    def __str__(self) -> str:
        return self.message


class TypeHintMissing(CompilerError):
    """
    An error raised when type hint cannot be found
    """
    def __init__(self, line: int, col: int, symbol_id: str = None):
        message = None
        if symbol_id is not None:
            message = "Type hint is missing for the symbol '%s'" % symbol_id
        super().__init__(line, col, message)


class InvalidType(CompilerError):
    """
    An error raised when a type that is not supported by Neo VM is used
    """
    def __init__(self, line: int, col: int, symbol_id: str = None):
        message = "Invalid type"
        if symbol_id is not None:
            message += ": '%s'" % symbol_id
        super().__init__(line, col, message)


class NotSupportedOperation(CompilerError):
    """
    An error raised when an operation that is not supported by Neo VM is used
    """
    def __init__(self, line: int, col: int, symbol_id: str):
        message = "The following operation is not supported: '%s'" % symbol_id
        super().__init__(line, col, message)


class UnresolvedReference(CompilerError):
    """
    An error raised when an undefined symbol is used
    """
    def __init__(self, line: int, col: int, symbol_id: str):
        message = "Unresolved reference '%s'" % symbol_id
        super().__init__(line, col, message)


class UnresolvedOperation(CompilerError):
    """
    An error raised when an undefined symbol is used
    """
    def __init__(self, line: int, col: int, type_id: str, operation_id: str):
        message = "Unresolved reference '%s' does not have a definition of '%s' operator" % (type_id, operation_id)
        super().__init__(line, col, message)


class MismatchedTypes(CompilerError):
    """
    An error raised when the evaluated and expected types are not the same
    """
    def __init__(self, line: int, col: int, expected_type_id: Union[str, Iterable[str]], actual_type_id: Union[str, Iterable[str]]):
        if isinstance(expected_type_id, str):
            expected_type_id = [expected_type_id]
        if isinstance(actual_type_id, str):
            actual_type_id = [actual_type_id]

        expected_types = join_args(expected_type_id)
        actual_types = join_args(actual_type_id)

        message = "Expected type '%s', got '%s' instead" % (expected_types, actual_types)
        super().__init__(line, col, message)


class TooManyReturns(CompilerError):
    """
    An error raised when a function returns a tuple
    """
    def __init__(self, line: int, col: int):
        message = "Too many returns"
        super().__init__(line, col, message)


class IncorrectNumberOfOperands(CompilerError):
    """
    An error raised when an operation is used with the wrong number of operands
    """
    def __init__(self, line: int, col: int, expected_count: int, actual_count: int):
        message = "Incorrect number of operands: expected '%s', got '%s' instead" % (expected_count, actual_count)
        super().__init__(line, col, message)


class UnexpectedArgument(CompilerError):
    """
    An error thrown when more arguments are used in a function than the number of arguments in the function's signature
    """
    def __init__(self, line: int, col: int):
        message = "Unexpected argument"
        super().__init__(line, col, message)


class UnfilledArgument(CompilerError):
    """
    An error thrown when less arguments are used in a function than the number of arguments in the function's signature
    """
    def __init__(self, line: int, col: int, param: str):
        message = "Parameter '%s' unfilled" % param
        super().__init__(line, col, message)


def join_args(iterable: Iterable[str]) -> str:
    return str.join("', '", iterable)
