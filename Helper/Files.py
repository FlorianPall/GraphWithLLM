import yaml
import json
import pandas as pd

CONFIG = "general.yml"

def config(config_part, log_callback, path_to_base="."):
    try:
        with open(path_to_base + "/src/config/" + CONFIG, 'r') as f:
            file = yaml.safe_load(f)
            return file[config_part]
    except yaml.YAMLError as e:
        log_callback(f"YAML Fehler: {e}")
    except FileNotFoundError:
        log_callback("Datei nicht gefunden. Path: " + "./src/config/" + CONFIG)

def cache(file, cache_folder, log_callback):
    try:
        with open('./src/Cache/' + cache_folder + '/' + file, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        log_callback("File not found!")
    except json.JSONDecodeError:
        log_callback("Invalid JSON format!")
    except KeyError as e:
        log_callback(f"Key not found: {e}")

def csv(file_path):
    return pd.read_csv(file_path,
                         encoding='utf-8',
                         quotechar='"',
                         escapechar='\\')
def csv_semicolon(file_path):
    return pd.read_csv(file_path,
                         encoding='utf-8',
                         sep=';',
                         quotechar='"',
                         escapechar='\\')

def write_json_cache(data, cache_folder, filename, log_callback):
    try:
        log_callback("Writing to file: " + filename)
        with open('./src/Cache/' + cache_folder + '/' + filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except Exception as e:
        log_callback(f"Error writing to file: {e}")

def write_txt_cache(data, cache_folder, filename, log_callback):
    try:
        log_callback("Writing to file: " + filename)
        with open('./src/Cache/' + cache_folder + '/' + filename, 'w', encoding='utf-8') as file:
            file.write(str(data))
    except Exception as e:
        log_callback(f"Error writing to file: {e}")

def get_prompt(prompt_name, log_callback):
    try:
        with open('./src/Prompts/' + prompt_name + '.txt', 'r') as file:
            return file.read()
    except FileNotFoundError:
        log_callback("File not found!")
    except json.JSONDecodeError:
        log_callback("Invalid JSON format!")
    except KeyError as e:
        log_callback(f"Key not found: {e}")
    return None