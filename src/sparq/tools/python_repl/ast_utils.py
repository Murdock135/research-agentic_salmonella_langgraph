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
    # Return early if the code is empty or only contains whitespace
    if not code or not code.strip():
        return None, "", None

    try:
        parsed_code = ast.parse(code)
    except SyntaxError as e:
        return None, "", e
    
    body = parsed_code.body
    if not body:
        return None, "", None

    last_node = body[-1]

    if isinstance(last_node, ast.Expr):
        # Last node is an expression
        if len(body) == 1:
            # Only one expression in the code
            return None, ast.unparse(last_node.value), None
        else:
            # Multiple statements, return all but the last as statements
            statements = [ast.unparse(node) for node in body[:-1]]
            expr = ast.unparse(last_node.value)
            return statements, expr, None

    else:
        # Last node is a statement
        statements = [ast.unparse(node) for node in body]
        return statements, "", None