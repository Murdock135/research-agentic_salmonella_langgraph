# utils.py

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

def get_df_heads(root_data_dir):
    import os
    import pandas as pd
    
    datasets = []
    df_heads_markdown = []
    text = ""
    
    for dirpath, dirname, files in os.walk(root_data_dir):
        if len(files) == 0:
            continue
        for file in files:
            file_path = os.path.join(dirpath, file)
            if file.endswith('.csv'):
                try:
                    df = load_dataset(file_path)
                    df_head = df.head().to_markdown()
                    df_heads_markdown.append(f"File: {file_path}\n{df_head}")
                    datasets.append(file_path)
                    
                    text += f"File: {file_path}\n{df_head}\n\n"
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
            
            if file.endswith('.xlsx'):
                try:
                    # Load all sheets
                    xls = pd.ExcelFile(file_path)
                    for sheet_name in xls.sheet_names:
                        df = pd.read_excel(xls, sheet_name=sheet_name)
                        df_head = df.head().to_markdown()
                        df_heads_markdown.append(f"File: {file_path}, Sheet: {sheet_name}\n{df_head}")
                        datasets.append(file_path)
                        
                        text += f"File: {file_path}, Sheet: {sheet_name}\n{df_head}\n\n"
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
    
    return text


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
    

# Tests
if __name__ == "__main__":
    import os
    from .config import Config
    
    config = Config()
    data_paths = config.get_selected_data_paths()
    mmg_dir = data_paths['mmg']
    mmg_data_path = os.path.join(mmg_dir, 'MMG2022_2020-2019Data_ToShare.xlsx')
    
    df = load_dataset(mmg_data_path, sheet_name='County')
    print(df.head().to_markdown())
    print("Data loaded successfully.")

    # Test get_data_paths_bash_tree
    tree_output = get_data_paths_bash_tree(config.SELECTED_DATA_DIR)
    print("Data paths tree:")
    print(tree_output)