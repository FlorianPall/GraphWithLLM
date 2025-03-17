import yaml
import json
import pandas as pd

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

def csv(file_path):
    return pd.read_csv(file_path,
                         encoding='utf-8',
                         # Verhindert, dass Pandas Kommas in Textfeldern als Trenner interpretiert
                         quotechar='"',
                         # Erlaubt Anführungszeichen in Textfeldern
                         escapechar='\\')

def write_json_cache(data, filename):
    try:
        print("Writing to file: " + filename)
        with open('./src/Cache/' + filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing to file: {e}")

def write_txt_cache(data, filename):
    try:
        print("Writing to file: " + filename)
        with open('./src/Cache/' + filename, 'w', encoding='utf-8') as file:
            file.write(str(data))
    except Exception as e:
        print(f"Error writing to file: {e}")

def get_prompt(prompt_name):
    try:
        with open('./src/Prompts/' + prompt_name + '.txt', 'r') as file:
            return file.read()
    except FileNotFoundError:
        print("File not found!")
    except json.JSONDecodeError:
        print("Invalid JSON format!")
    except KeyError as e:
        print(f"Key not found: {e}")
    return None