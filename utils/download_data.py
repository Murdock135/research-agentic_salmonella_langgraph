# This script downloads datasets from a specified Hugging Face repository.
# Docs: https://huggingface.co/docs/huggingface_hub/en/guides/download#download-an-entire-repository
# Optional: Read https://huggingface.co/docs/datasets/en/cache to understand how to load the downloaded datasets.

from huggingface_hub import snapshot_download

from ..load_env import load_env_vars
import os

REPO_ID = "zayanhugsAI"
datasets = [
    "census_population",
    "naco",
    "nors",
    "pulsenet",
    "socioecono_salmonella",
    "map_the_meal_gap",
    "social_vulnerability_index"
]

# OUTPUT_DIR = "data"

def download_dataset_repo(repo_id, dataset_name, token, output_dir=None):
    """
    Download a specific dataset from the Hugging Face Hub.
    
    Args:
        repo_id (str): The repository ID on Hugging Face Hub.
        dataset_name (str): The name of the dataset to download.
        output_dir (str): The directory where the dataset will be saved.
    """
    snapshot_download(repo_id=f"{repo_id}/{dataset_name}", repo_type="dataset", local_dir=output_dir if output_dir is not None else None, token=token)

def main():
    """
    Main function to download all datasets.
    """
    load_env_vars()
    HF_TOKEN = os.getenv("HF_TOKEN")
    print(f"Using Hugging Face token: {HF_TOKEN}")

    if HF_TOKEN is None:
        raise ValueError("HF_TOKEN environment variable is not set. Please set it before running the script.")
    

    for dataset in datasets:
        print(f"Downloading dataset: {dataset}")
        download_dataset_repo(REPO_ID, dataset, token=HF_TOKEN)
        print(f"Dataset {dataset} downloaded successfully.")

if __name__ == "__main__":
    main()