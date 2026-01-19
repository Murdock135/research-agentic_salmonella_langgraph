_PERSISTENT_NAMESPACE = {}

def get_persistent_namespace() -> dict:
    """
    Retrieves the persistent namespace used for code execution.
    
    :return: The persistent namespace dictionary.
    :rtype: dict[Any, Any]
    """
    return _PERSISTENT_NAMESPACE

def clean_namespace(namespace: dict):
    """
    Cleans the given namespace by removing any built-in or special variables.
    
    :param namespace: The namespace dictionary to clean.
    :type namespace: dict
    """
    keys_to_remove = [key for key in namespace if key.startswith("__") and key.endswith("__")]
    for key in keys_to_remove:
        del namespace[key]