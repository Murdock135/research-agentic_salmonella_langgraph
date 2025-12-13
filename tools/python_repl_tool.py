from typing import Dict, Tuple, Optional
import multiprocessing
import ast
import time
from contextlib import redirect_stderr, redirect_stdout
import io

from pydantic import BaseModel
from langchain_core.tools import tool


# =========================================================================
# OUTPUT SCHEMA
# NOTE: Adopt this later into output_schemas.py
# =========================================================================

class ExecutionResult(BaseModel):
    code: str
    stdout: str
    stderr: str
    return_value: str
    success: bool
    execution_time: float
    execution_mode: str

# =========================================================================
# PERSISTENT GLOBALS FOR EXECUTION CONTEXT
# =========================================================================

_GLOBALS: Dict = {"__builtins__": __builtins__}


def extract_last_expr(code: str) -> Tuple[Optional[str], str]:
    """
    Check if the last line is an expression and extract it.
    Returns: (last_expression, remaining_code)
    """
    try:
        tree = ast.parse(code)
        if not tree.body:
            return None, code
        
        last_node = tree.body[-1]
        
        if isinstance(last_node, ast.Expr):
            lines = code.strip().split('\n')
            last_line = lines[-1].strip()
            rest = '\n'.join(lines[:-1]) if len(lines) > 1 else ""
            return last_line, rest
        else:
            return None, code
    except SyntaxError:
        return None, code    

def worker(
        code: str,
        globals: Dict,
        queue: multiprocessing.Queue,
        execution_mode: str
) -> None:
    result = {
        "stdout": "",
        "stderr": "",
        "return_value": None,
        "success": False
    }

    try:
        last_expr, remaining_code = extract_last_expr(code)

        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            if remaining_code:
                exec(remaining_code, globals)

            if last_expr:
                result["return_value"] = eval(last_expr, globals)

        result["stdout"] = stdout_buffer.getvalue()
        result["stderr"] = stderr_buffer.getvalue()
        result["success"] = True
    except Exception as e:
        result["stderr"] += str(e)
    finally:
        queue.put(result)

def _execute_code(
        code: str,
        globals: Dict,
        execution_mode: str,
        timeout: int = 30,
):
    start_time = time.time()

    queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=worker, 
        args=(code, globals, queue, execution_mode)
        )
    
    # Start the process
    process.start()

    # Wait for the process to finish or timeout
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        return ExecutionResult(
            code=code,
            stdout="",
            stderr="Execution timed out.",
            return_value="",
            success=False,
            execution_time=time.time() - start_time,
            execution_mode=execution_mode
        )
    else:
        result = queue.get()
        return ExecutionResult(
            code=code,
            stdout=result.get("stdout"),
            stderr=result.get("stderr"),
            return_value=str(result.get("return_value")),
            success=result.get("success"),
            execution_time=time.time() - start_time,
            execution_mode=execution_mode
        )
    
@tool
def execute_code_isolated(code: str) -> ExecutionResult:
    pass

@tool
def execute_code_persistent(code: str) -> ExecutionResult:
    pass