_PERSISTENT_NAMESPACE = {}

def get_persistent_namespace() -> dict:
    """
    Retrieves the persistent namespace used for code execution.
    
    :return: The persistent namespace dictionary.
    :rtype: dict[Any, Any]
    """
    return _PERSISTENT_NAMESPACE

def reset_persistent_namespace():
    """
    Resets the persistent namespace to an empty state.
    :return: None
    :rtype: None
    """
    global _PERSISTENT_NAMESPACE
    _PERSISTENT_NAMESPACE.clear()