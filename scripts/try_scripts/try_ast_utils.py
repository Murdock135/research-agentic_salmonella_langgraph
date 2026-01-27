from sparq.tools.python_repl.ast_utils import extract_last_expression

def main():
    code = "a = 1\nb = 2\na + b"
    statements, last_expr, error = extract_last_expression(code)
    print("Statements:", statements)
    print("Last Expression:", last_expr)
    print("Error:", error)