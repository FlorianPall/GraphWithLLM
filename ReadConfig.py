import yaml

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

