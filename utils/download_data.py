# This script downloads datasets from a specified Hugging Face repository.
# Docs: https://huggingface.co/docs/huggingface_hub/en/guides/download#download-an-entire-repository
# Optional: Read https://huggingface.co/docs/datasets/en/cache and https://huggingface.co/docs/datasets/load_hub#configurationsto understand how to load the downloaded datasets.

from huggingface_hub import snapshot_download

from config.load_env import load_env_vars
from .helpers import dump_dict_to_json
from config.config import Config
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
        token (str): The Hugging Face token for authentication.
        output_dir (str): The directory where the dataset will be saved.
    """
    path = snapshot_download(repo_id=f"{repo_id}/{dataset_name}", repo_type="dataset", local_dir=output_dir if output_dir is not None else None, token=token)
    return path

def main():
    """
    Main function to download all datasets.
    """
    load_env_vars()
    config = Config()
    HF_TOKEN = os.getenv("HF_TOKEN")
    print(f"Using Hugging Face token: {HF_TOKEN}")

    if HF_TOKEN is None:
        raise ValueError("HF_TOKEN environment variable is not set. Please set it before running the script.")
    

    manifest = {}

    for dataset in datasets:
        manifest[dataset] = None  # Placeholder for dataset metadata


        print(f"Downloading dataset: {dataset}")
        cache_location = download_dataset_repo(REPO_ID, dataset, token=HF_TOKEN)
        print(f"Dataset {dataset} downloaded successfully.")

        # Add cache location to manifest
        manifest[dataset] = {
            "cache_location": cache_location,
            "repo_id": f"{REPO_ID}/{dataset}"
        }

    project_root = config.BASE_DIR
    dump_dict_to_json(manifest, project_root + "/data_manifest.json")

if __name__ == "__main__":
    main()