_PERSISTENT_NAMESPACE = {}

def get_persistent_namespace() -> dict:
    """
    Retrieves the persistent namespace used for code execution.
    
    :return: The persistent namespace dictionary.
    :rtype: dict[Any, Any]
    """
    return _PERSISTENT_NAMESPACE