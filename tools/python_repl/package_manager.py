from pathlib import Path
import tomllib

DEFAULT_PACKAGE_LIST = {
    "blocked": [ "os", "sys", "subprocess", "shutil", "socket", "multiprocessing", "threading", "ctypes", "signal" ],
    "safe": [ "math", "json", "re", "datetime", "functools", "itertools", "collections", "random", "string", "time", "statistics" ],
    "whitelisted": [ "numpy", "pandas", "statsmodels", "scipy", "matplotlib", "seaborn", "plotly" ],
}

def load_package_config(config_path: str = "config/package_config.toml") -> dict:
    """
    Docstring for load_package_config
    
    :param config_path: Description
    :type config_path: str
    :return: Description
    :rtype: dict
    """
    config_file = Path(config_path)

    # Return default if config file does not exist and exit early
    if not config_file.exists():
        return DEFAULT_PACKAGE_LIST

    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)

            return {
                "blocked": config["stdlib"]["blocked"],
                "safe": config["stdlib"]["safe"],
                "whitelisted": config["third_party"]["whitelisted"],
            }
    except Exception as e:
        print(f"Error loading package config: {e}. \nUsing default package list.\n")
        return DEFAULT_PACKAGE_LIST
