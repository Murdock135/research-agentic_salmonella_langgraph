from sparq.tools.python_repl.executor import execute_code

from langchain.tools import tool

@tool
def execute_code_persistent(code: str, persist_namespace: bool = True, timeout: int = 10) -> dict:
    """
    Executes Python code in a REPL environment.

    Args:
        code (str): The Python code to execute.
        persist_namespace (bool): Whether to persist the namespace across executions.
        timeout (int): Maximum time in seconds to allow for code execution.

    Returns:
        dict: A dictionary containing the output, error message (if any), and success status.
    """
    return execute_code(code, persist_namespace=persist_namespace, timeout=timeout)

