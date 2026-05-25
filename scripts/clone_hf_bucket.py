#!/usr/bin/env python3
"""Download all files from hf://buckets/KingOfThoughtFleuren/Aetherius-storage into HFbucket/."""
import os
from huggingface_hub import HfFileSystem

HF_TOKEN = os.environ["HF_TOKEN"]
BUCKET_PATH = "hf://buckets/KingOfThoughtFleuren/Aetherius-storage"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "HFbucket")


def download_recursive(fs: HfFileSystem, remote_path: str, local_path: str) -> None:
    os.makedirs(local_path, exist_ok=True)
    for item in fs.ls(remote_path, detail=True):
        name = item["name"].rstrip("/").split("/")[-1]
        remote_item = item["name"]
        local_item = os.path.join(local_path, name)
        if item["type"] == "directory":
            download_recursive(fs, remote_item, local_item)
        else:
            print(f"  {remote_item}  ->  {local_item}")
            fs.get(remote_item, local_item)


if __name__ == "__main__":
    print(f"Connecting to {BUCKET_PATH} ...")
    fs = HfFileSystem(token=HF_TOKEN)
    print(f"Downloading into {OUTPUT_DIR} ...")
    download_recursive(fs, BUCKET_PATH, OUTPUT_DIR)
    print("Done.")
