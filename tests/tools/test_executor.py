import unittest

from sparq.tools.python_repl.executor import *

class TestExecutor(unittest.TestCase):
    def test_basic_execution(self):
        code = "a = 1\nb = 2\na + b"
        result = execute_code(code, persist_namespace=False, timeout=5)
        self.assertTrue(result.success)
        self.assertEqual(result.output, "3")
        self.assertIn("a", result.namespace)
        self.assertIn("b", result.namespace)
        self.assertEqual(result.namespace["a"], 1)
        self.assertEqual(result.namespace["b"], 2)

    # def test_importing(self):
    #     code = "import math\nmath.sqrt(16)"
    #     result = execute_code(code, persist_namespace=False, timeout=5)
    #     self.assertTrue(result.success)
    #     self.assertEqual(result.output, "4.0")
    #     self.assertIn("math", result.namespace)
    #     self.assertTrue(hasattr(result.namespace["math"], "sqrt"))