# TODO: Implement a function to find the package directory of SPARQ. This can be useful for locating resources relative to the package, such as default configuration files or prompts.
from pathlib import Path

def find_package_dir() -> Path | None:
    """Returns the first directory where 'pyproject.toml' is found."""
    current_dir = Path(__file__).parent
    while current_dir != current_dir.parent:
        if (current_dir / "pyproject.toml").exists():
            return current_dir
        current_dir = current_dir.parent
    return None