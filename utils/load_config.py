import yaml
import os

def load_config(url: str):
    with open(url, 'r') as file:
        config = yaml.safe_load(file)
    return config