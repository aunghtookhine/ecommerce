import json, yaml, os, dotenv

dotenv.load_dotenv(override=True)

with open(os.getenv("API_JSON_FILENAME"), "r") as json_file:
    json_data = json.load(json_file)

with open(os.getenv("API_YAML_FILENAME"), "w") as yaml_file:
    yaml_file.write(yaml.dump(json_data))
