
from langchain_core.tools import tool, InjectedToolCallId
from langchain_community.tools import Tool
from langchain_experimental.utilities import PythonREPL
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from typing import Annotated
python_repl = PythonREPL()


@tool
def load_dataset(file_path, sheet_name=None):
    """
    Loads a dataset from either a CSV or an Excel sheet.
    Args:
        file_path (str): Path to the dataset file.
        sheet_name (str, optional): Name of the Excel sheet to load. Defaults to None.
    Returns:
    """
    import pandas as pd
    global df
    if file_path.endswith('.csv'):
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return f"PythonError: {e}"
    elif file_path.endswith('.xlsx') and sheet_name:
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            return f"PythonError: {e}"
    else:
        raise ValueError("Unsupported file format or missing sheet name for Excel file.")
    
    return f"Loaded dataset into variable `df`.\n\nPreview:\n{df.head().to_markdown()}"
    
@tool
def get_sheet_names(file_path):
    """
    Returns the sheet names of an Excel file. (Only works if argument is an excel file)
    Args:
        file_path (str): The path to the Excel file.
    Returns:
        list: A list of sheet names.
    """
    import pandas as pd
    
    sheet_names = "Sheet names:\n"
    if not file_path.endswith('.xlsx'):
        return ("Provided file is not an excel file.")
    
    try:
        excel_file = pd.ExcelFile(file_path)
    except Exception as e:
        return f"PythonError: {e}"
    
    for sheet_name in excel_file.sheet_names:
        sheet_names += f"- {sheet_name}\n"
        
    return sheet_names


def filesystemtools(working_dir, selected_tools=['write_file']):
    from langchain_community.agent_toolkits import FileManagementToolkit
    
    TOOLS = [
    'write_file',
    'read_file',
    'copy_file',
    'file_search',
    'list_directory',
    ]
    
    # check tools
    for tool in selected_tools:
        if tool not in TOOLS:
            raise ValueError(f"The tool, {tool} is not supported.\n"
                             "Please select from {TOOLS}"
                             )
    
    # If selected_tools is not a list, convert to a list        
    if not isinstance(selected_tools, list):
        selected_tools=[selected_tools]
    
    tools = FileManagementToolkit(
        root_dir=working_dir,
        selected_tools=selected_tools
    ).get_tools()
    
    return tools

def getpythonrepltool():
    pythonREPLtool = Tool(
        name="python_repl",
        func=python_repl.run,
        description="A Python REPL that can execute Python code. Use this to run Python code and get the result.",
    )
    
    return pythonREPLtool

@tool
def run_code(
    code: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Run Python code in a REPL environment.
    Use this to execute steps of the plan that require Python code execution.
    """
    from langchain_experimental.utilities import PythonREPL
    python_repl = PythonREPL()
    
    return Command(
        update={
            "results": python_repl.run(code),
            "messages": [
                ToolMessage(
                    content=f"Executed code: {code}",
                    tool_call_id=tool_call_id,
                    tool_name="python_repl",
                )
            ]
            }
    )

@tool
def get_cached_dataset_path(repo_id: str):
    """ Get the path to a cached dataset from Hugging Face Hub.
    Args:
        repo_id (str): The repository ID of the dataset on Hugging Face Hub.
    Returns:
        Path: The path to the cached dataset.
    """
    from huggingface_hub import snapshot_download
    import os
    from pathlib import Path
    
    # Load HF Token
    HF_TOKEN = os.getenv("HF_TOKEN")
    if HF_TOKEN is None:
        raise ValueError("HF_TOKEN environment variable is not set. Please set it before running the script.")
    
    # get path to cached dataset
    path = snapshot_download(repo_id=repo_id, repo_type="dataset", token=HF_TOKEN)

    return Path(path)

@tool
def get_glob_files(repo_id):
    """
    Get list of files in a directory of all patterns"""

    path = get_cached_dataset_path.invoke(repo_id)

    for _ in path.rglob("*"):
        if not _.is_file():
            raise ValueError(f"Path {path} is not a file. Please provide a valid file path.")
        
        print(_)

if __name__ == "__main__":
    # Example usage of the tools
    from config import Config
    config = Config()
    repo_ids = config.get_data_repoIDs
