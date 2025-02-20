import yaml
import json

CONFIG = "general.yml"

def config(config_part):
    try:
        with open("./src/config/" + CONFIG, 'r') as f:
            file = yaml.safe_load(f)
            return file[config_part]
    except yaml.YAMLError as e:
        print(f"YAML Fehler: {e}")
    except FileNotFoundError:
        print("Datei nicht gefunden. Path: " + "./src/config/" + CONFIG)

def cache(file):
    try:
        with open('./src/Cache/' + file, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("File not found!")
    except json.JSONDecodeError:
        print("Invalid JSON format!")
    except KeyError as e:
        print(f"Key not found: {e}")

