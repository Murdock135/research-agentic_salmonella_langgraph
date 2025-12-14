import ast
import multiprocessing as mp

from typing import Optional, List, Tuple


def extract_last_expression(code: str) -> Tuple[Optional[List[str]], str, Optional[SyntaxError]]:
    """
    Docstring for extract_last_expression
    
    :param code: Description
    :type code: str
    :return: Description
    :rtype: Tuple[List[str] | None, str, SyntaxError | None]

    - Catches SyntaxError
    """

    try:
        parsed_code = ast.parse(code)
    except SyntaxError as e:
        return None, "", e
    
    body = parsed_code.body
    last_node = body[-1]

    lines = code.strip().splitlines()
    if isinstance(last_node, ast.Expr):

        statements = lines[:-1] if len(lines) > 1 else None
        expr = lines[-1].strip()

        return (statements, expr, None)
    else:
        return (lines, "", None)


def execute_code_in_new_process(code: str, namespace: dict, timeout: int = 10) -> Optional[str]:
    """
    Executes the given Python code and returns the output or error message.

    Args:
        code (str): The Python code to execute.
    """

    statements, expr, syntax_error = extract_last_expression(code)
    if syntax_error:
        return f"SyntaxError: {syntax_error}"
    
    queue = mp.Queue()
    process = mp.Process(
        target=_target, 
        args=(
            statements,
            expr,
            queue,
            namespace
            )
        )
    
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        return "Error: Execution timed out."
    else:
        result = queue.get()
        return result

def _target(statements: Optional[List[str]], expr: str, queue: mp.Queue, namespace: dict):
    """
    Docstring for _target
    
    :param statements: Description
    :type statements: Optional[List[str]]
    :param expr: Description
    :type expr: str
    :param queue: Description
    :type queue: mp.Queue
    :param namespace: Description
    :type namespace: dict

    - Catches Any Exception (SyntaxError should be caught earlier)
    """
    try:
        # If there are statements, execute them with namespace 
        if statements:
            exec("\n".join(statements), namespace)

        if expr != "":
            result = eval(expr, namespace)
        else:
            result = None
    
    # Catches Any Exception (SyntaxError should be caught earlier)
    except Exception as e:
        queue.put(f"Error: {e}")

    finally:
        queue.put(repr(result))

