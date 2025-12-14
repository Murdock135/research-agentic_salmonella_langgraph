from .executor import _execute_code_in_new_process
from .package_manager import load_package_config

_PERSISTENT_NAMESPACE = {}

def execute_code(code: str, persist_namespace: bool = False, timeout: int = 10) -> dict:
    if persist_namespace:
        namespace = _PERSISTENT_NAMESPACE # Use module-level namespace for persistence
    else:
        namespace = {} # Fresh namespace for non-persistent execution
    
    return _execute_code_in_new_process(code, timeout=timeout, new_namespace=namespace, persist_namespace=persist_namespace)

if __name__ == "__main__":    
    print("Testing tool python repl tool")

    code_snippet = """
x = 10
y = 20
x + y
                    """
    output = execute_code(code_snippet, persist_namespace=True)
    print(output.get("output"))  # Expected: 30

    output = execute_code("x * 2", persist_namespace=True)
    print(output.get("output"))  # Expected: 20
