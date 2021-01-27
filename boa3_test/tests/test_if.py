from boa3.boa3 import Boa3
from boa3.exception.CompilerError import MismatchedTypes
from boa3.model.type.type import Type
from boa3.neo.vm.opcode.Opcode import Opcode
from boa3.neo.vm.type.Integer import Integer
from boa3_test.tests.boa_test import BoaTest
from boa3_test.tests.test_classes.testengine import TestEngine


class TestIf(BoaTest):

    default_folder: str = 'test_sc/if_test'

    def test_if_constant_condition(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01'
            + b'\x00'
            + Opcode.PUSH0      # a = 0
            + Opcode.STLOC0
            + Opcode.PUSH1
            + Opcode.JMPIFNOT   # if True
            + Integer(4).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH2     # a = a + 2
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return a
            + Opcode.RET
        )

        path = self.get_contract_path('ConstantCondition.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(2, result)

    def test_if_variable_condition(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01'
            + b'\x01'
            + Opcode.PUSH0      # a = 0
            + Opcode.STLOC0
            + Opcode.LDARG0
            + Opcode.JMPIFNOT   # if arg0
            + Integer(4).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH2      # a = a + 2
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return a
            + Opcode.RET
        )

        path = self.get_contract_path('VariableCondition.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main', True)
        self.assertEqual(2, result)
        result = self.run_smart_contract(engine, path, 'Main', False)
        self.assertEqual(0, result)

    def test_if_mismatched_type_condition(self):
        path = self.get_contract_path('MismatchedTypeCondition.py')
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_if_no_condition(self):
        path = self.get_contract_path('IfWithoutCondition.py')

        with self.assertRaises(SyntaxError):
            output = Boa3.compile(path)

    def test_if_no_body(self):
        path = self.get_contract_path('IfWithoutBody.py')

        with self.assertRaises(SyntaxError):
            output = Boa3.compile(path)

    def test_nested_if(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x02'
            + Opcode.PUSH0      # c = 0
            + Opcode.STLOC0
            + Opcode.PUSH0      # d = c
            + Opcode.STLOC1
            + Opcode.LDARG0
            + Opcode.JMPIFNOT   # if arg0
            + Integer(13).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH2      # c = c + 2
            + Opcode.STLOC0
            + Opcode.LDARG1
            + Opcode.JMPIFNOT   # if arg1
            + Integer(4).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH3      # d = d + 3
            + Opcode.STLOC1
            + Opcode.PUSH2      # c = c + d
            + Opcode.LDLOC1
            + Opcode.ADD
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return c
            + Opcode.RET
        )

        path = self.get_contract_path('NestedIf.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main', True, True)
        self.assertEqual(5, result)
        result = self.run_smart_contract(engine, path, 'Main', True, False)
        self.assertEqual(2, result)
        result = self.run_smart_contract(engine, path, 'Main', False, True)
        self.assertEqual(0, result)
        result = self.run_smart_contract(engine, path, 'Main', False, False)
        self.assertEqual(0, result)

    def test_if_else(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01'
            + b'\x01'
            + Opcode.PUSH0      # a = 0
            + Opcode.STLOC0
            + Opcode.LDARG0
            + Opcode.JMPIFNOT   # if arg0
            + Integer(6).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH2      # a = a + 2
            + Opcode.STLOC0
            + Opcode.JMP        # else
            + Integer(4).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH10     # a = 10
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return a
            + Opcode.RET
        )
        path = self.get_contract_path('IfElse.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main', True)
        self.assertEqual(2, result)
        result = self.run_smart_contract(engine, path, 'Main', False)
        self.assertEqual(10, result)

    def test_else_no_body(self):
        path = self.get_contract_path('ElseWithoutBody.py')

        with self.assertRaises(SyntaxError):
            output = Boa3.compile(path)

    def test_if_elif(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01'
            + b'\x01'
            + Opcode.PUSH0      # a = 0
            + Opcode.STLOC0
            + Opcode.LDARG0
            + Opcode.JMPIFNOT   # if arg0
            + Integer(6).to_byte_array(min_length=1)
            + Opcode.PUSH2      # a = a + 2
            + Opcode.STLOC0
            + Opcode.JMP
            + Integer(7).to_byte_array(min_length=1)
            + Opcode.LDARG0
            + Opcode.JMPIFNOT   # elif arg0
            + Integer(4).to_byte_array(min_length=1)
            + Opcode.PUSH10     # a = 10
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return a
            + Opcode.RET
        )

        path = self.get_contract_path('IfElif.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main', True)
        self.assertEqual(2, result)
        result = self.run_smart_contract(engine, path, 'Main', False)
        self.assertEqual(0, result)

    def test_elif_no_condition(self):
        path = self.get_contract_path('ElifWithoutCondition.py')

        with self.assertRaises(SyntaxError):
            output = Boa3.compile(path)

    def test_elif_no_body(self):
        path = self.get_contract_path('ElifWithoutBody.py')

        with self.assertRaises(SyntaxError):
            output = Boa3.compile(path)

    def test_if_relational_condition(self):
        jmp_address = Integer(4).to_byte_array(min_length=1, signed=True)

        expected_output = (
            Opcode.INITSLOT
            + b'\x01'
            + b'\x01'
            + Opcode.PUSH0      # a = 0
            + Opcode.STLOC0
            + Opcode.LDARG0
            + Opcode.PUSH10
            + Opcode.LT
            + Opcode.JMPIFNOT   # if c < 10
            + jmp_address
            + Opcode.PUSH2      # a = a + 2
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return a
            + Opcode.RET
        )

        path = self.get_contract_path('RelationalCondition.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main', 5)
        self.assertEqual(2, result)
        result = self.run_smart_contract(engine, path, 'Main', 10)
        self.assertEqual(0, result)

    def test_if_multiple_branches(self):
        twenty = Integer(20).to_byte_array()
        expected_output = (
            Opcode.INITSLOT
            + b'\x01'
            + b'\x01'
            + Opcode.LDARG0
            + Opcode.PUSH0
            + Opcode.LT
            + Opcode.JMPIFNOT       # if arg0 < 0
            + Integer(6).to_byte_array(min_length=1)
            + Opcode.PUSH0          # a = 0
            + Opcode.STLOC0
            + Opcode.JMP
            + Integer(35).to_byte_array(min_length=1)
            + Opcode.LDARG0
            + Opcode.PUSH5
            + Opcode.LT
            + Opcode.JMPIFNOT       # elif arg0 < 5
            + Integer(6).to_byte_array(min_length=1)
            + Opcode.PUSH5          # a = 5
            + Opcode.STLOC0
            + Opcode.JMP
            + Integer(26).to_byte_array(min_length=1)
            + Opcode.LDARG0
            + Opcode.PUSH10
            + Opcode.LT
            + Opcode.JMPIFNOT       # elif arg0 < 10
            + Integer(6).to_byte_array(min_length=1)
            + Opcode.PUSH10         # a = 10
            + Opcode.STLOC0
            + Opcode.JMP
            + Integer(17).to_byte_array(min_length=1)
            + Opcode.LDARG0
            + Opcode.PUSH15
            + Opcode.LT
            + Opcode.JMPIFNOT       # elif arg0 < 15
            + Integer(6).to_byte_array(min_length=1)
            + Opcode.PUSH15         # a = 15
            + Opcode.STLOC0
            + Opcode.JMP            # else
            + Integer(8).to_byte_array(min_length=1)
            + Opcode.PUSHDATA1      # a = 20
            + Integer(len(twenty)).to_byte_array()
            + twenty
            + Opcode.CONVERT
            + Type.int.stack_item
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return a
            + Opcode.RET
        )

        path = self.get_contract_path('MultipleBranches.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main', -10)
        self.assertEqual(0, result)
        result = self.run_smart_contract(engine, path, 'Main', 2)
        self.assertEqual(5, result)
        result = self.run_smart_contract(engine, path, 'Main', 7)
        self.assertEqual(10, result)
        result = self.run_smart_contract(engine, path, 'Main', 13)
        self.assertEqual(15, result)
        result = self.run_smart_contract(engine, path, 'Main', 17)
        self.assertEqual(20, result)
        result = self.run_smart_contract(engine, path, 'Main', 23)
        self.assertEqual(20, result)

    def test_if_expression_variable_condition(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01'
            + b'\x01'
            + Opcode.LDARG0
            + Opcode.JMPIFNOT   # a = 2 if arg0 else 3
            + Integer(5).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH2      # 2
            + Opcode.JMP        # else
            + Integer(3).to_byte_array(min_length=1, signed=True)
            + Opcode.PUSH3      # 3
            + Opcode.STLOC0
            + Opcode.LDLOC0     # return a
            + Opcode.RET
        )
        path = self.get_contract_path('IfExpVariableCondition.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'Main', True)
        self.assertEqual(2, result)
        result = self.run_smart_contract(engine, path, 'Main', False)
        self.assertEqual(3, result)

    def test_if_expression_without_else_branch(self):
        path = self.get_contract_path('IfExpWithoutElse.py')

        with self.assertRaises(SyntaxError):
            output = Boa3.compile(path)

    def test_if_expression_mismatched_types(self):
        path = self.get_contract_path('MismatchedIfExp.py')
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_inner_if_else(self):
        path = self.get_contract_path('InnerIfElse.py')
        self.compile_and_save(path)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'main', 4, 3, 2, 1)
        self.assertEqual(3, result)

        result = self.run_smart_contract(engine, path, 'main', 4, 3, 1, 2)
        self.assertEqual(8, result)

        result = self.run_smart_contract(engine, path, 'main', 4, 1, 2, 3)
        self.assertEqual(10, result)

        result = self.run_smart_contract(engine, path, 'main', 1, 2, 4, 3)
        self.assertEqual(1, result)

        result = self.run_smart_contract(engine, path, 'main', 1, 2, 3, 4)
        self.assertEqual(11, result)

        result = self.run_smart_contract(engine, path, 'main', 1, 3, 2, 4)
        self.assertEqual(22, result)

    def test_if_is_instance_condition(self):
        path = self.get_contract_path('IfIsInstanceCondition.py')
        self.compile_and_save(path)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'example', 4)
        self.assertEqual(4, result)

        result = self.run_smart_contract(engine, path, 'example', '123')
        self.assertEqual(-1, result)

        result = self.run_smart_contract(engine, path, 'example', -70)
        self.assertEqual(-70, result)

        result = self.run_smart_contract(engine, path, 'example', True)
        self.assertEqual(-1, result)

    def test_if_else_is_instance_condition(self):
        path = self.get_contract_path('IfElseIsInstanceCondition.py')
        self.compile_and_save(path)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'example', 4)
        self.assertEqual(4, result)

        result = self.run_smart_contract(engine, path, 'example', '123')
        self.assertEqual(-1, result)

        result = self.run_smart_contract(engine, path, 'example', -70)
        self.assertEqual(-70, result)

        result = self.run_smart_contract(engine, path, 'example', True)
        self.assertEqual(-1, result)

    def test_if_else_is_instance_condition_with_union_variable(self):
        path = self.get_contract_path('IfElseIsInstanceConditionWithUnionVariable.py')
        self.compile_and_save(path)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'example', 4,
                                         expected_result_type=bytes)
        self.assertEqual(b'\x04', result)

        result = self.run_smart_contract(engine, path, 'example', '123',
                                         expected_result_type=bytes)
        self.assertEqual(b'123', result)

        result = self.run_smart_contract(engine, path, 'example', -70,
                                         expected_result_type=bytes)
        self.assertEqual(Integer(-70).to_byte_array(), result)

        result = self.run_smart_contract(engine, path, 'example', True,
                                         expected_result_type=bytes)
        self.assertEqual(b'\x01', result)

    def test_if_else_multiple_is_instance_condition_with_union_variable(self):
        path = self.get_contract_path('IfElseMultipleIsInstanceConditionWithUnionVariable.py')
        self.compile_and_save(path)

        engine = TestEngine()
        result = self.run_smart_contract(engine, path, 'example', 4)
        self.assertEqual(16, result)

        result = self.run_smart_contract(engine, path, 'example', [b'123456', b'789'])
        self.assertEqual(6, result)

        result = self.run_smart_contract(engine, path, 'example', -70)
        self.assertEqual(4900, result)

        result = self.run_smart_contract(engine, path, 'example', [])
        self.assertEqual(1, result)

        result = self.run_smart_contract(engine, path, 'example', b'True')
        self.assertEqual(4, result)

    def test_variable_in_if_scopes(self):
        path = self.get_contract_path('VariablesInIfScopes.py')
        self.compile_and_save(path)

        engine = TestEngine()

        result = self.run_smart_contract(engine, path, 'main', 1, expected_result_type=bool)
        self.assertEqual(False, result)

        result = self.run_smart_contract(engine, path, 'main', 2, expected_result_type=bool)
        self.assertEqual(True, result)

        result = self.run_smart_contract(engine, path, 'main', 3, expected_result_type=bool)
        self.assertEqual(False, result)

        result = self.run_smart_contract(engine, path, 'main', 4, expected_result_type=bool)
        self.assertEqual(True, result)

        result = self.run_smart_contract(engine, path, 'main', 5, expected_result_type=bool)
        self.assertEqual(False, result)

        result = self.run_smart_contract(engine, path, 'main', 6, expected_result_type=bool)
        self.assertEqual(False, result)

        result = self.run_smart_contract(engine, path, 'main', 7, expected_result_type=bool)
        self.assertEqual(False, result)

        result = self.run_smart_contract(engine, path, 'main', 8, expected_result_type=bool)
        self.assertEqual(False, result)
