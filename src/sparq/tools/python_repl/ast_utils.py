import ast
from typing import List, Optional, Tuple

def extract_last_expression(code: str) -> Tuple[Optional[List[str]], str, Optional[SyntaxError]]:
    """
    Extracts the last expression from the given Python code.

    Args:
        code (str): The Python code to analyze.
    
    Returns:
        Tuple[Optional[List[str]], str, Optional[SyntaxError]]: A tuple containing the list of statements before the last expression (or None if there are none), the last expression as a string, and a SyntaxError if one occurred (or None if no error occurred).
    """
    try:
        parsed_code = ast.parse(code)
    except SyntaxError as e:
        return None, "", e
    
    body = parsed_code.body
    if not body:
        return None, "", None

    last_node = body[-1]

    lines = code.strip().splitlines()
    if isinstance(last_node, ast.Expr):

        statements = lines[:-1] if len(lines) > 1 else None
        expr = lines[-1].strip()

        return (statements, expr, None)
    else:
        return (lines, "", None)
