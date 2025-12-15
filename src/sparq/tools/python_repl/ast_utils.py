import ast
from typing import List, Optional, Tuple

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
