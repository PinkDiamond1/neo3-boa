import ast
from typing import List, Dict, Optional, Any

from boa3.analyser.astanalyser import IAstAnalyser
from boa3.exception import CompilerError
from boa3.exception.CompilerError import CompilerError as Error
from boa3.model.method import Method
from boa3.model.expression import IExpression
from boa3.model.module import Module
from boa3.model.symbol import ISymbol
from boa3.model.operation.binaryop import BinaryOp
from boa3.model.operation.operator import Operator
from boa3.model.operation.unaryop import UnaryOp
from boa3.model.type.type import Type, IType


class TypeAnalyser(IAstAnalyser, ast.NodeVisitor):
    """
    This class is responsible for the type checking of the code

    The methods with the name starting with 'visit_' are implementations of methods from the :class:`NodeVisitor` class.
    These methods are used to walk through the Python abstract syntax tree.

    :ivar type_errors: a list with the found type errors. Empty by default.
    :ivar modules: a list with the analysed modules. Empty by default.
    :ivar symbols: a dictionary that maps the global symbols.
    """

    def __init__(self, ast_tree: ast.AST, symbol_table: Dict[str, ISymbol]):
        super().__init__(ast_tree)
        self.type_errors: List[Exception] = []
        self.modules: Dict[str, Module] = {}
        self.symbols: Dict[str, ISymbol] = symbol_table

        self.__current_method: Method = None

        self.visit(self._tree)

    def _log_error(self, error: Error):
        self.errors.append(error)
        raise error

    @property
    def __current_method_id(self) -> str:
        """
        Get the string identifier of the current method

        :return: The name identifier of the method. If the current method is None, returns None.
        :rtype: str or None
        """
        if self.__current_method in self.symbols.values():
            index = list(self.symbols.values()).index(self.__current_method)
            return list(self.symbols.keys())[index]

    def get_type(self, value: Any) -> IType:
        """
        Returns the type of the given value.

        :param value: value to get the type
        :return: Returns the :class:`IType` of the the type of the value. `Type.none` by default.
        """
        if isinstance(value, IType):
            return value
        elif isinstance(value, IExpression):
            return value.type
        elif isinstance(value, bool):
            return Type.bool
        elif isinstance(value, int):
            return Type.int
        elif isinstance(value, str):
            return Type.str

        return Type.none

    def visit_Module(self, module: ast.Module):
        """
        Visitor of the module node

        Performs the type checking in the body of the method

        :param module: the python ast module node
        """
        for stmt in module.body:
            self.visit(stmt)

    def visit_FunctionDef(self, function: ast.FunctionDef):
        """
        Visitor of the function node

        Performs the type checking in the body of the function

        :param function: the python ast function definition node
        """
        self.visit(function.args)
        method = self.symbols[function.name]
        self.__current_method = method

        for stmt in function.body:
            self.visit(stmt)
        self.__current_method = None

    def visit_arguments(self, arguments: ast.arguments):
        """
        Verifies if each argument of a function has a type annotation

        :param arguments: the python ast function arguments node
        """
        for arg in arguments.args:
            self.visit(arg)

        # continue to walk through the tree
        self.generic_visit(arguments)

    def visit_arg(self, arg: ast.arg):
        """
        Verifies if the argument of a function has a type annotation

        :param arg: the python ast arg node
        """
        if arg.annotation is None:
            self._log_error(
                CompilerError.TypeHintMissing(arg.lineno, arg.col_offset, symbol_id=arg.arg)
            )

        # continue to walk through the tree
        self.generic_visit(arg)

    def visit_Return(self, ret: ast.Return):
        """
        Verifies if the return of the function is the same type as the return type annotation

        :param ret: the python ast return node
        """
        if ret.value is not None:
            # multiple returns are not allowed
            if isinstance(ret.value, ast.Tuple):
                self._log_error(
                    CompilerError.TooManyReturns(ret.lineno, ret.col_offset)
                )
                return
            # it is returning something, but there is no type hint for return
            elif self.__current_method.return_type is Type.none:
                self._log_error(
                    CompilerError.TypeHintMissing(ret.lineno, ret.col_offset, symbol_id=self.__current_method_id)
                )
                return
            # TODO: check if the type of return is the same as in the type hint
        elif self.__current_method.return_type is not Type.none:
            # the return is None, but the type hint value type is not None
            self._log_error(
                CompilerError.MismatchedTypes(
                    ret.lineno, ret.col_offset,
                    actual_type_id=Type.none.identifier,
                    expected_type_id=self.__current_method.return_type.identifier)
            )

        # continue to walk through the tree
        self.generic_visit(ret)

    def visit_Assign(self, assign: ast.Assign):
        """
        Verifies if it is a multiple assignments statement

        :param assign: the python ast variable assignment node
        """
        # multiple assignments
        if len(assign.targets) > 1:
            self._log_error(
                CompilerError.NotSupportedOperation(assign.lineno, assign.col_offset, 'Multiple variable assignments')
            )

        # multiple assignments with tuples
        if isinstance(assign.targets[0], ast.Tuple):
            self._log_error(
                CompilerError.NotSupportedOperation(assign.lineno, assign.col_offset, 'Multiple variable assignments')
            )

    def visit_BinOp(self, bin_op: ast.BinOp) -> Optional[IType]:
        """
        Verifies if the types of the operands are valid to the operation

        If the operation is valid, changes de Python operator by the Boa operator in the syntax tree

        :param bin_op: the python ast binary operation node
        :return: the type of the result of the operation if the operation is valid. Otherwise, returns None
        :rtype: IType or None
        """
        operator: Operator = self.visit(bin_op.op)
        r_operand = self.visit(bin_op.right)
        l_operand = self.visit(bin_op.left)

        if not isinstance(operator, Operator):
            # the operator is invalid or it was not implemented yet
            self._log_error(
                CompilerError.UnresolvedReference(bin_op.lineno, bin_op.col_offset, type(operator).__name__)
            )

        try:
            operation: BinaryOp = self.get_bin_op(operator, r_operand, l_operand)
            if operation is None:
                self._log_error(
                    CompilerError.NotSupportedOperation(bin_op.lineno, bin_op.col_offset, operator)
                )
            elif operation in [BinaryOp.Concat, BinaryOp.Pow, BinaryOp.Div]:
                # TODO: concat and exponentiation not implemented yet
                # number float division is not supported by the Neo VM
                self._log_error(
                    CompilerError.NotSupportedOperation(bin_op.lineno, bin_op.col_offset, operator)
                )
            else:
                bin_op.op = operation
                return operation.result_type
        except CompilerError.MismatchedTypes as raised_error:
            expected_types = raised_error.args[2]
            actual_types = raised_error.args[3]
            self._log_error(
                CompilerError.MismatchedTypes(bin_op.lineno, bin_op.col_offset, expected_types, actual_types)
            )

    def get_bin_op(self, operator: Operator, right: Any, left: Any) -> BinaryOp:
        """
        Returns the binary operation specified by the operator and the types of the operands

        :param operator: the operator
        :param right: right operand
        :param left: left operand

        :return: Returns the corresponding :class:`BinaryOp` if the types are valid.
        :raise MismatchedTypes: raised if the types aren't valid for the operator
        """
        l_type: IType = self.get_type(left)
        r_type: IType = self.get_type(right)

        actual_types: str = "%s', '%s" % (l_type.identifier, r_type.identifier)
        operation = None
        expected_op = None

        # Arithmetic operators
        if operator == Operator.Plus:
            if r_type == Type.int and l_type == Type.int:
                # number addition
                operation = BinaryOp.Add
            elif r_type == Type.str and l_type == Type.str:
                # string concatenation
                operation = BinaryOp.Concat
            else:
                expected_op = BinaryOp.Add
        elif operator == Operator.Minus:
            if r_type == Type.int and l_type == Type.int:
                # number subtraction
                operation = BinaryOp.Sub
            else:
                expected_op = BinaryOp.Sub
        elif operator == Operator.Mult:
            if r_type == Type.int and l_type == Type.int:
                # number multiplication
                operation = BinaryOp.Mul
            else:
                expected_op = BinaryOp.Mul
        elif operator == Operator.IntDiv:
            if r_type == Type.int and l_type == Type.int:
                # number integer division
                operation = BinaryOp.IntDiv
            else:
                expected_op = BinaryOp.IntDiv
        elif operator == Operator.Div:
            if r_type == Type.int and l_type == Type.int:
                # number integer division
                operation = BinaryOp.IntDiv
            else:
                expected_op = BinaryOp.IntDiv
        elif operator == Operator.Mod:
            if r_type == Type.int and l_type == Type.int:
                # number modulo
                operation = BinaryOp.Mod
            else:
                expected_op = BinaryOp.Mod
        elif operator == Operator.Pow:
            if r_type == Type.int and l_type == Type.int:
                # number exponentiation
                operation = BinaryOp.Pow
            else:
                expected_op = BinaryOp.Pow

        if expected_op is not None:
            expected_types: str = "%s', '%s" % (expected_op.left_op_type.identifier, expected_op.right_op_type.identifier)
            raise CompilerError.MismatchedTypes(0, 0, expected_types, actual_types)
        return operation

    def visit_UnaryOp(self, un_op: ast.UnaryOp) -> Optional[IType]:
        """
        Verifies if the type of the operand is valid to the operation

        If the operation is valid, changes de Python operator by the Boa operator in the syntax tree

        :param un_op: the python ast unary operation node
        :return: the type of the result of the operation if the operation is valid. Otherwise, returns None
        :rtype: IType or None
        """
        operator: Operator = self.visit(un_op.op)
        operand = self.visit(un_op.operand)

        try:
            operation: UnaryOp = self.get_un_op(operator, operand)
            if operation is None:
                self._log_error(
                    CompilerError.NotSupportedOperation(un_op.lineno, un_op.col_offset, operator)
                )
            else:
                un_op.op = operation
                return operation.result_type
        except CompilerError.MismatchedTypes as raised_error:
            expected_types = raised_error.args[2]
            actual_types = raised_error.args[3]
            # raises the exception with the line/col info
            self._log_error(
                CompilerError.MismatchedTypes(un_op.lineno, un_op.col_offset, expected_types, actual_types)
            )

    def get_un_op(self, operator: Operator, operand: Any) -> UnaryOp:
        """
        Returns the binary operation specified by the operator and the types of the operands

        :param operator: the operator
        :param operand: the operand

        :return: Returns the corresponding :class:`UnaryOp` if the types are valid.
        :raise MismatchedTypes: raised if the types aren't valid for the operator
        """
        op_type: IType = self.get_type(operand)

        actual_type: str = op_type.identifier
        operation = None
        expected_op = None

        if operator == Operator.Plus:
            if op_type == Type.int:
                # number positive operation
                operation = UnaryOp.Positive
            else:
                expected_op = UnaryOp.Positive
        elif operator == Operator.Minus:
            if op_type == Type.int:
                # number negative operation
                operation = UnaryOp.Negative
            else:
                expected_op = UnaryOp.Negative

        if expected_op is not None:
            expected_type: str = expected_op.result_type.identifier
            raise CompilerError.MismatchedTypes(0, 0, expected_type, actual_type)
        return operation

    def visit_Add(self, add: ast.Add) -> Operator:
        """
        Returns the operator equivalent to Python add operator

        :param add: the python ast '+' operand node
        :return: returns the equivalent Boa :class:`Operator`
        """
        return Operator.Plus

    def visit_Sub(self, sub: ast.Sub) -> Operator:
        """
        Returns the operator equivalent to Python sub operator

        :param sub: the python ast '-' operand node
        :return: returns the equivalent Boa :class:`Operator`
        """
        return Operator.Minus

    def visit_Mult(self, mult: ast.Mult) -> Operator:
        """
        Returns the operator equivalent to Python mult operator

        :param mult: the python ast '*' operand node
        :return: returns the equivalent Boa :class:`Operator`
        """
        return Operator.Mult

    def visit_FloorDiv(self, floor_div: ast.FloorDiv) -> Operator:
        """
        Returns the operator equivalent to Python floor div operator

        :param floor_div: the python ast '//' operand node
        :return: returns the equivalent Boa :class:`Operator`
        """
        return Operator.IntDiv

    def visit_Mod(self, mod: ast.Mod) -> Operator:
        """
        Returns the operator equivalent to Python floor div operator

        :param mod: the python ast '%' operand node
        :return: returns the equivalent Boa :class:`Operator`
        """
        return Operator.Mod

    def visit_UAdd(self, add: ast.UAdd) -> Operator:
        """
        Returns the operator equivalent to Python add operator

        :param add: the python ast '+' operand node
        :return: returns the equivalent Boa :class:`Operator`
        """
        return Operator.Plus

    def visit_USub(self, sub: ast.USub) -> Operator:
        """
        Returns the operator equivalent to Python sub operator

        :param sub: the python ast '-' operand node
        :return: returns the equivalent Boa :class:`Operator`
        """
        return Operator.Minus

    def visit_Num(self, num: ast.Num) -> int:
        """
        Verifies if the number is an integer

        :param num: the python ast number node
        :return: returns the value of the number
        """
        if not isinstance(num.n, int):
            # only integer numbers are allowed
            self._log_error(
                CompilerError.InvalidType(num.lineno, num.col_offset, symbol_id=type(num.n).__name__)
            )
        return num.n

    def visit_Str(self, str: ast.Str) -> str:
        """
        Visitor of literal string node

        :param str: the python ast string node
        :return: the value of the string
        """
        return str.s

    def visit_NameConstant(self, constant: ast.NameConstant) -> Any:
        """
        Visitor of constant names node

        :param constant: the python ast name constant node
        :return: the value of the constant
        """
        return constant.value
