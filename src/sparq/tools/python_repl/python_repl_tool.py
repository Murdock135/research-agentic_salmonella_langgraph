from langchain.tools import tool

from sparq.tools.python_repl.schemas import PythonREPLInput
from sparq.tools.python_repl.executor import execute_code


@tool
def python_repl_tool(input: PythonREPLInput) -> dict:
    """
    Executes the given Python code in a REPL environment.
    Supports variable persistence across executions and automatic installation of 
    white-listed packages, if missing.

    Args:
        input (PythonREPLInput): The input containing the code to execute, whether to persist the namespace, and the timeout.

    Returns:
        dict: The result of the code execution, including output, error, namespace, and success status.
    """
    return execute_code(input.code, persist_namespace=input.persist_namespace, timeout=input.timeout)