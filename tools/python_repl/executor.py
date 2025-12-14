import multiprocessing as mp

from typing import Optional, List

from tools.python_repl.ast_utils import extract_last_expression

# TODO:
"""todo:
- Convert the execute_code into a langchain tool.
- Implment structured output.
- Allow for third party library imports.
"""

def _execute_code_in_new_process(code: str, timeout: int = 10, new_namespace: Optional[dict] = None, persist_namespace: bool = False) -> dict:
    """
    Executes the given Python code and returns the output or error message.

    Args:
        code (str): The Python code to execute.
    """

    statements, expr, syntax_error = extract_last_expression(code)
    if syntax_error:
        return {
            "output": "",
            "error": f"SyntaxError: {syntax_error}",
            "namespace": new_namespace,
            "success": False,
        }
    
    queue = mp.Queue()
    process = mp.Process(
        target=_target, 
        args=(
            statements,
            expr,
            queue,
            new_namespace
            )
        )
    
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        result = {
            "output": "",
            "error": "Error: Code execution timed out.",
            "namespace": new_namespace,
            "success": False,
        }
    else:
        result = queue.get()

    # Update the namespace if execution was successful and persistence is desired
    if result["success"] and persist_namespace:
            new_namespace.update(result["namespace"])
    
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
    result = {
        "output": "",
        "error": "",
        "namespace": namespace,
        "success": False,
    }

    try:
        # If there are statements, execute them with namespace 
        if statements:
            exec("\n".join(statements), namespace)

        if expr != "":
            result["output"] = eval(expr, namespace)

        result["success"] = True
    
    # Catches Any Exception (SyntaxError should be caught earlier)
    except Exception as e:
        result["error"] += f"{type(e).__name__}: {e}"

    finally:
        queue.put(result)
