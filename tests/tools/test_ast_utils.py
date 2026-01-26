import unittest

from sparq.tools.python_repl.ast_utils import extract_last_expression

class TestASTUtils(unittest.TestCase):
    def test_basic_extraction(self):
        code = "a = 1\nb = 2\na + b"
        statements, last_expr, error = extract_last_expression(code)
        self.assertEqual(last_expr, "a + b")
        self.assertEqual(statements, ["a = 1", "b = 2"])
        self.assertIsNone(error)
    
    def test_syntax_error(self):
        code = "a = 1\nb = 2\na +"
        statements, last_expr, error = extract_last_expression(code)
        self.assertIsNone(statements)
        self.assertEqual(last_expr, "")
        self.assertIsInstance(error, SyntaxError)

    def test_no_statements(self):
        code = "a + b"
        statements, last_expr, error = extract_last_expression(code)
        self.assertIsNone(statements)
        self.assertEqual(last_expr, "a + b")
        self.assertIsNone(error)

    def test_last_node_not_expression(self):
        code = "a = 1\nb = 2"
        statements, last_expr, error = extract_last_expression(code)
        self.assertEqual(statements, ["a = 1", "b = 2"])
        self.assertEqual(last_expr, "")
        self.assertIsNone(error)

    def test_empty_code(self):
        code = ""
        statements, last_expr, error = extract_last_expression(code)
        self.assertIsNone(statements)
        self.assertEqual(last_expr, "")
        self.assertIsNone(error)
    
    def test_function_definition(self):
        code = "def foo():\n    return 42\nfoo()"
        statements, last_expr, error = extract_last_expression(code)
        self.assertEqual(statements, ["def foo():", "    return 42"])
        self.assertEqual(last_expr, "foo()")
        self.assertIsNone(error)

    