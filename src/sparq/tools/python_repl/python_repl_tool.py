from langchain.tools import tool

from sparq.tools.python_repl.schemas import PythonREPLInput
from sparq.tools.python_repl.executor import execute_code
from sparq.tools.python_repl.schemas import OutputSchema


@tool(args_schema=PythonREPLInput)
def python_repl_tool(code: str, persist_namespace: bool = False, timeout: int = 10) -> OutputSchema:
    """
    Executes the given Python code in a REPL environment.
    Supports variable persistence across executions and automatic installation of 
    white-listed packages, if missing.

    Args:
        code: The Python code to execute.
        persist_namespace: Whether to persist the namespace across executions.
        timeout: The maximum time in seconds to allow for code execution.

    Returns:
        OutputSchema: The result of the code execution, including output, error, namespace, and success status.
    """
    return execute_code(code, persist_namespace=persist_namespace, timeout=timeout)

def test_python_repl_tool():
    """
    Basic tests for the python_repl_tool function.
    """
    # Test 1: Basic arithmetic with persistence
    input_data = {"code": "x = 5\ny = 10\nx + y", "persist_namespace": True, "timeout": 5}
    output = python_repl_tool.invoke(input_data)
    
    assert output.success is True, f"Expected success=True, got {output.success}"
    assert output.output == "15", f"Expected output='15', got '{output.output}'"
    assert "x" in output.namespace, "Variable 'x' not found in namespace"
    assert "y" in output.namespace, "Variable 'y' not found in namespace"
    assert output.namespace["x"] == 5, f"Expected x=5, got {output.namespace['x']}"
    assert output.namespace["y"] == 10, f"Expected y=10, got {output.namespace['y']}"
    
    print("✓ Test 1 passed: Basic arithmetic with persistence")
    
    # Test 2: Error handling
    input_data = {"code": "undefined_var", "persist_namespace": False, "timeout": 5}
    output = python_repl_tool.invoke(input_data)
    
    assert output.success is False, "Expected failure for undefined variable"
    assert output.error is not None, "Expected error information"
    assert output.error.type == "NameError", f"Expected NameError, got {output.error.type}"
    
    print("✓ Test 2 passed: Error handling")
    
    # Test 3a: Non-persistent namespace - first execution
    input_data = {"code": "temp = 100\ntemp", "persist_namespace": False, "timeout": 5}
    output = python_repl_tool.invoke(input_data)
    
    assert output.success is True, "Expected success for isolated execution"
    assert output.output == "100", f"Expected output='100', got '{output.output}'"
    
    # Test 3b: Non-persistent namespace - verify variable doesn't persist
    input_data = {"code": "temp", "persist_namespace": False, "timeout": 5}
    output = python_repl_tool.invoke(input_data)
    
    assert output.success is False, "Expected failure - 'temp' should not exist in new isolated execution"
    assert output.error is not None, "Expected error information"
    assert output.error.type == "NameError", f"Expected NameError for undefined 'temp', got {output.error.type}"
    
    print("✓ Test 3 passed: Non-persistent namespace isolation verified")
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_python_repl_tool()