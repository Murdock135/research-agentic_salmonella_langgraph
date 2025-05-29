from langchain.tools import tool
from langchain_community.tools import Tool
from langchain_experimental.utilities import PythonREPL

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
    python_repl = PythonREPL()
    pythonREPLtool = Tool(
        name="python_repl",
        func=python_repl.run,
        description="A Python REPL that can execute Python code. Use this to run Python code and get the result.",
    )
    
    return pythonREPLtool
    