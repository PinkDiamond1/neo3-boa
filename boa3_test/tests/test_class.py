from boa3.neo.vm.type.String import String
from boa3_test.tests.boa_test import BoaTest
from boa3_test.tests.test_classes.testengine import TestEngine


class TestClass(BoaTest):

    def test_notification_get_variables(self):
        path = '%s/boa3_test/test_sc/class_test/NotificationGetVariables.py' % self.dirname
        output, manifest = self.compile_and_save(path)

        abi_hash = manifest['abi']['hash']
        script = bytearray()
        for x in range(2, len(abi_hash), 2):
            script.append(int(abi_hash[x:x + 2], 16))
        script.reverse()

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'script_hash', [])
        self.assertEqual(len(engine.notifications), 0)
        if isinstance(result, str):
            result = String(result).to_bytes()
        self.assertEqual(bytes(20), result)

        result = self.run_smart_contract(engine, path, 'event_name', [])
        self.assertEqual(len(engine.notifications), 0)
        self.assertEqual('', result)

        result = self.run_smart_contract(engine, path, 'state', [])
        self.assertEqual(len(engine.notifications), 0)
        self.assertEqual([], result)

        result = self.run_smart_contract(engine, path, 'script_hash', [1])
        self.assertEqual(len(engine.notifications), 1)
        self.assertEqual(script, result)

        result = self.run_smart_contract(engine, path, 'event_name', [1])
        self.assertEqual(len(engine.notifications), 1)
        self.assertEqual('notify', result)

        result = self.run_smart_contract(engine, path, 'state', [1])
        self.assertEqual(len(engine.notifications), 1)
        self.assertEqual([1], result)

        result = self.run_smart_contract(engine, path, 'state', ['1'])
        self.assertEqual(len(engine.notifications), 1)
        self.assertEqual(['1'], result)

    def test_notification_set_variables(self):
        path = '%s/boa3_test/test_sc/class_test/NotificationSetVariables.py' % self.dirname
        output, manifest = self.compile_and_save(path)

        abi_hash = manifest['abi']['hash']
        script = bytearray()
        for x in range(2, len(abi_hash), 2):
            script.append(int(abi_hash[x:x + 2], 16))
        script.reverse()

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'script_hash', script)
        if isinstance(result, str):
            result = String(result).to_bytes()
        self.assertEqual(script, result)

        result = self.run_smart_contract(engine, path, 'event_name', 'unit test')
        self.assertEqual('unit test', result)

        result = self.run_smart_contract(engine, path, 'state', (1, 2, 3))
        self.assertEqual([1, 2, 3], result)