# utils.py
from pandas import DataFrame

def load_text(file_path):
    """Loads text from a file."""
    with open(file_path, 'r') as f:
        text = f.read()

    return text

def save_text(text, filepath, time_stamp=True):
    import datetime
    
    # Save response
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    if time_stamp:
        file_path = file_path + timestamp

    with open(file_path, 'w') as f:
        f.write(text)

def load_dataset(file_path, sheet_name=None):
    import pandas as pd

    """
    Loads a dataset from either a CSV or an Excel sheet.
    Args:
        file_path (str): Path to the dataset file.
        sheet_name (str, optional): Name of the Excel sheet to load. Defaults to None.
    Returns:
    """
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') and sheet_name:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    else:
        raise ValueError("Unsupported file format or missing sheet name for Excel file.")

def get_data_paths(root):
    tree_str = ""
    for dirpath, dirnames, filenames in os.walk(root):
        print("Directory:", dirpath)
        print("Subdirectories:", dirnames)
        print("Files:", filenames)
        
        tree_str += f"Directory: {dirpath}\n"
        tree_str += f"Subdirectories: {dirnames}\n"
        tree_str += f"Files: {filenames}\n"
        tree_str += "\n"
        
    return tree_str

def get_data_paths_bash_tree(root):
    import subprocess

    try:
        output = subprocess.check_output(['tree', root], text=True)
    except Exception as e:
        output = f"Error running tree command: {e}"
    return output

def get_df_summary(df: DataFrame):
    summary = DataFrame({
        'Column': df.columns,
        'Non-Null Count': df.notnull().sum(),
        'Dtype': df.dtypes
    })
    
    return summary.to_markdown()
    
def get_df_summary_from_excel(file_path) -> dict[str, str]:
    import pandas as pd
    
    """
    Loads an Excel file and returns the summaries of all sheets in markdown format.
    
    Args:
        file_path (str): Path to the Excel file.
        
    Returns:
        str: Markdown formatted string of sheet summaries.
    """
    xls = pd.ExcelFile(file_path)
    df_summaries = {}
    
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        try:
            summary = get_df_summary(df)
        except Exception as e:
            raise Exception(f"could not summarise: {file_path}'s sheet {sheet_name} to markdown")
            
        df_summaries[sheet_name] = summary
    
    return df_summaries

def get_df_summaries_from_manifest(manifest: dict[str, dict[str, str]]) -> dict[str, str]:
    """
    Extracts data summaries from a manifest dictionary.
    
    Args:
        manifest (dict): Dictionary containing dataset information.
        
    Returns:
        dict: Dictionary with sheet names as keys and data summaries (columns, non null counts, dtypes) in markdown format as values.
    """
    from tools.tools import find_csv_excel_files, get_cached_dataset_path
    from pathlib import Path
    import pandas as pd
    
    df_summaries = {}
    
    for dataset, info in manifest.items():
        df_summaries[dataset] = {} # create sub dictionary for each dataset
        repo_id = info.get('repo_id')
        location: Path = get_cached_dataset_path.invoke(repo_id)
        
        files = find_csv_excel_files.invoke({'root_dir': location})
        for file in files:
            # get excels and csvs
            if file.suffix == '.xlsx' or file.suffix == '.csv':
                subdata_name = file.name # file name
                df_summaries[dataset][subdata_name] = None # initialize for storing df.head later
                # Get head
                if file.suffix == '.csv':
                    df = pd.read_csv(file)
                    df_summaries[dataset][subdata_name] = get_df_summary(df)
                elif file.suffix == '.xlsx':
                    df_heads : dict[str, str] = get_df_summary_from_excel(file) # df_heads is a dict with {sheet: df_head_markdown}
                    df_summaries[dataset][subdata_name] = df_heads
                        
    return df_summaries
                

def get_llm(model='gpt-4o', provider='openai'):
    if provider=='openai':
        from langchain.chat_models import init_chat_model
        return init_chat_model(model=model, model_provider=provider)
    
    elif provider=='openrouter':
        import os
        from langchain_openai import ChatOpenAI
        
        try:
            api_key = os.getenv('OPENROUTER_API_KEY')
        except:
            raise ValueError("OPENROUTER API NOT FOUND")
        
        try:
            base_url = os.getenv('OPENROUTER_BASE_URL')
        except:
            raise ValueError("OPENROUTER BASE URL NOT FOUND")
        
        model = model or "meta-llama/llama-4-maverick:free"
        return ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=base_url,
            model_name=model
        )
        
    
    elif provider == 'ollama':
        from langchain_ollama import ChatOllama
        from ollama import ResponseError
        
        try:
            llm = ChatOllama(model=model)
            return llm
        except ResponseError as e:
            choice = input(f"Model {model} not found. Do you want to pull it? (y/n): ")
            if choice.lower() == 'y':
                pull_ollama_model(model)
                return ChatOllama(model=model)
            else:
                raise ValueError(f"Model {model} not found and not pulled.")
    
    else:
        raise ValueError(f"Provider '{provider} not supported. Please choose 'openai', 'openrouter', or 'ollama'.")


def pull_ollama_model(model_name: str) -> None:
    import subprocess
    from config import Config
    import os
    
    config = Config()
    project_dir = config.BASE_DIR
    download_script = os.path.join(project_dir, 'utils', 'dl_ollama_model.sh')
    if not os.path.exists(download_script):
        raise FileNotFoundError(f"Download script not found at {download_script}. Please check the path.")

    result = subprocess.run([download_script, model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("STDOUT:\n", result.stdout)
    if result.returncode != 0:
        print("Error:\n", result.stderr)
    else:
        print(f"Model {model_name} pulled successfully.")
    
        
def get_user_query(args=None, config=None):
    if args is not None and args.test:
        if config is None:
            user_query = "What are the main factors contributing to salmonella rates in Missouri in a statistical sense?"
        else:
            user_query = config.get('test_query')
            if user_query is None:
                raise ValueError("Test query not found in config.")
            
        print("Using test query: ", user_query)
    else:
        user_query = input("Enter your query:\n")

    return user_query

def parse_args():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Agentic system for QA")
    parser.add_argument('--test', action="store_true", help="Use a test query")
    parser.add_argument('--ollama', action="store_true", help="Use ollama backend")
    parser.add_argument('--openrouter', action="store_true", help="Use openrouter backend")
    parser.add_argument("--model", type=str, help="Model name")
    return parser.parse_args()

def dump_dict_to_json(dict, save_path):
    """
    Dumps a dictionary to a JSON file.
    
    Args:
        dict (dict): The dictionary to dump.
        save_path (str): The path where the JSON file will be saved.
    """
    import json
    with open(save_path, 'w') as f:
        json.dump(dict, f, indent=4)
    print(f"Dictionary dumped to {save_path}")
    
def load_data_manifest(path_to_manifest_file) -> dict[str, dict[str, str]]:
    """
    Load a data manifest file and return its contents.
    """
    import json
    import os
    
    if not os.path.exists(path_to_manifest_file):
        raise FileNotFoundError(f"Manifest file not found: {path_to_manifest_file}")
    
    with open(path_to_manifest_file, 'r') as f:
        manifest: dict = json.load(f)
    
    return manifest

def get_data_repoIDs(path_to_manifest_file):
    """
    Get the repository IDs of datasets from the manifest file.
    """
    manifest = load_data_manifest(path_to_manifest_file)
    repo_ids = {dataset: info['repo_id'] for dataset, info in manifest.items() if 'repo_id' in info}
    
    return repo_ids

# Tests
if __name__ == "__main__":
    import os
    from .config import Config
    
    config = Config()
    manifest_path = os.path.join(config.BASE_DIR, "data_manifest.json")
    manifest_dict= load_data_manifest(manifest_path)
    
    df_heads = get_df_summaries_from_manifest(manifest_dict)
    
    print(df_heads)