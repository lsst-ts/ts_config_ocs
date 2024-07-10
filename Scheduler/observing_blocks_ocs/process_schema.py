import json
import yaml


def process_schema(args):
    data = json.load(open(args.file))
    schema =data["_schema_comment"]
    configuration_schema = yaml.dump(schema, sort_keys=False)
    data["configuration_schema"] = configuration_schema
    json.dump(data, open(args.file, "w"), indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)
    args = parser.parse_args()
    process_schema(args)
