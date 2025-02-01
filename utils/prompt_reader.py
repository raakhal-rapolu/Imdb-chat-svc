import yaml

def load_prompts(yaml_file="prompts/prompt.yaml"):
    with open(yaml_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


