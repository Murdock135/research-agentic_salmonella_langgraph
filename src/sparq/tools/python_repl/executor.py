import multiprocessing as mp
import traceback

from typing import Optional, List

from sparq.tools.python_repl.ast_utils import extract_last_expression
from sparq.tools.python_repl.namespace import get_persistent_namespace, clean_namespace
from sparq.tools.python_repl.package_manager import PackageUtils as putils
from sparq.tools.python_repl.schemas import OutputSchema, ExceptionInfo

# TODO:
"""todo:
- Implment structured output.
"""

def execute_code(code: str, persist_namespace: bool = False, timeout: int = 10) -> OutputSchema:
    if persist_namespace:
        namespace = get_persistent_namespace() # Use module-level namespace for persistence
    else:
        namespace = {} # Fresh namespace for non-persistent execution
    
    result = _execute_code_in_new_process(code, timeout=timeout, new_namespace=namespace, persist_namespace=persist_namespace)

    # On import error, install the package if whitelisted and retry execution
    if result.error and "ModuleNotFoundError" in result.error.message:
        missing_package = putils.extract_package_name_error(result.error.message)
        if missing_package:
            install_result = putils.install_package(missing_package)
            if install_result["success"]:
                # Retry execution after successful installation
                result = _execute_code_in_new_process(code, timeout=timeout, new_namespace=namespace, persist_namespace=persist_namespace)
            else:
                # Update error with installation failure info
                result.error.extra_context["package_install_failed"] = {
                    "package": missing_package,
                    "message": install_result["message"]
                }
    
    return result


def _execute_code_in_new_process(code: str, timeout: int = 10, new_namespace: Optional[dict] = None, persist_namespace: bool = False) -> OutputSchema:
    """
    Executes the given Python code and returns the output or error message.

    Args:
        code (str): The Python code to execute.
    """

    statements, expr, syntax_error = extract_last_expression(code)
    if syntax_error:
        return OutputSchema(
            output="",
            error=ExceptionInfo(
                type="SyntaxError",
                message=str(syntax_error),
                traceback="",
                extra_context={}
            ),
            namespace=new_namespace or {},
            success=False
        )
    
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
        result = OutputSchema(
            output="",
            error=ExceptionInfo(
                type="TimeoutError",
                message="Code execution timed out.",
                traceback="",
                extra_context={"timeout_seconds": timeout}
            ),
            namespace=new_namespace or {},
            success=False
        )
    else:
        result = queue.get()

    # Update the namespace if execution was successful and persistence is desired
    if result.success and persist_namespace:
            new_namespace.update(result.namespace)
    
    return result

def _target(statements: Optional[List[str]], expr: str, queue: mp.Queue, namespace: dict):
    """
    Target function for multiprocessing execution.
    
    :param statements: List of Python statements to execute
    :type statements: Optional[List[str]]
    :param expr: Final expression to evaluate
    :type expr: str
    :param queue: Queue for returning results
    :type queue: mp.Queue
    :param namespace: Execution namespace
    :type namespace: dict

    - Catches Any Exception (SyntaxError should be caught earlier)
    """
    try:
        # If there are statements, execute them with namespace 
        if statements:
            exec("\n".join(statements), namespace)

        output = ""
        if expr != "":
            output = str(eval(expr, namespace))

        # Clean the namespace by removing any built-in or special variables
        clean_namespace(namespace)

        result = OutputSchema(
            output=output,
            error=None,
            namespace=namespace,
            success=True
        )
    
    # Catches Any Exception (SyntaxError should be caught earlier)
    except Exception as e:

        # Clean the namespace by removing any built-in or special variables
        clean_namespace(namespace)
        
        result = OutputSchema(
            output="",
            error=ExceptionInfo(
                type=type(e).__name__,
                message=str(e),
                traceback=traceback.format_exc(),
                extra_context={}
            ),
            namespace=namespace,
            success=False
        )

    finally:
        queue.put(result)

if __name__ == "__main__":    
    print("Testing tool python repl tool")

    code_snippet = """
x = 10
y = 20
x + y3
                    """
    output = execute_code(code_snippet, persist_namespace=True)
    print(output)

    # output = execute_code("x * 2", persist_namespace=True)
    # print(output)
