from sparq.tools.python_repl.ast_utils import extract_last_expression
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    code = "a = 1\nb = 2\na + b"
    statements, last_expr, error = extract_last_expression(code)
    logger.debug("Statements: %s", statements)
    logger.debug("Last Expression: %s", last_expr)
    logger.debug("Error: %s", error)

    code = """
def foo(x):
    return x * 2

x = 5
f = foo(x)
f
"""
    statements, last_expr, error = extract_last_expression(code)
    logger.debug("Statements: %s", statements)
    logger.debug("Last Expression: %s", last_expr)
    logger.debug("Error: %s", error)

if __name__ == "__main__":
    main()