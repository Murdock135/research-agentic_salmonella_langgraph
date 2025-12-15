from pathlib import Path
import tomllib
import subprocess
import sys

DEFAULT_PACKAGE_LIST = {
    "blocked": [ "os", "sys", "subprocess", "shutil", "socket", "multiprocessing", "threading", "ctypes", "signal" ],
    "safe": [ "math", "json", "re", "datetime", "functools", "itertools", "collections", "random", "string", "time", "statistics" ],
    "whitelisted": [ "numpy", "pandas", "statsmodels", "scipy", "matplotlib", "seaborn", "plotly" ],
}

def install_package(package_name: str) -> dict:
    """
    Install a package if it's whitelisted.
    
    :param package_name: Description
    :type package_name: str
    :return: Description
    :rtype: bool
    """
    if not is_whitelisted_package(package_name, load_package_config()):
        print(f"Package '{package_name}' is not whitelisted for installation.")
        return {
            "success": False,
            "message": f"Package '{package_name}' is not whitelisted for installation."
        }
    
    if is_installed_package(package_name):
        print(f"Package '{package_name}' is already installed.")
        return {
            "success": True,
            "message": f"Package '{package_name}' is already installed."
        }
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {
            "success": True,
            "message": f"Package '{package_name}' installed successfully."
        }
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package '{package_name}': {e}")
        return {
            "success": False,
            "message": f"Failed to install package '{package_name}': {e}"
        }


def load_package_config(config_path: str = None) -> dict:
    """
    Docstring for load_package_config
    
    :param config_path: Description
    :type config_path: str
    :return: Description
    :rtype: dict
    """
    heirarchy_paths = [
        Path(config_path) if config_path else None,
        Path.home() / ".config" / "sparq" / "package_config.toml",
        Path(__file__).parent / "package_config.toml",
    ]

    # Find the first existing config file in the heirarchy
    config_file = None
    for path in heirarchy_paths:
        if path and path.exists():
            config_file = path
            break
    
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
    
def is_whitelisted(package_name: str, package_config: dict) -> bool:
    """
    Docstring for is_whitelisted
    
    :param package_name: Description
    :type package_name: str
    :param package_config: Description
    :type package_config: dict
    :return: Description
    :rtype: bool
    """
    if package_name in package_config["blocked"]:
        return False
    
    return (package_name in package_config["safe"] or package_name in package_config["whitelisted"])

def is_installed(package_name: str) -> bool:
    """
    Docstring for is_installed
    
    :param package_name: Description
    :type package_name: str
    :return: Description
    :rtype: bool
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

