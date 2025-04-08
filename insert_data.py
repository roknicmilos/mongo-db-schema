import json
import sys

import mongo


def load_data_from_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def insert_document(with_valid_data=True):
    filepath = "valid-data.json" if with_valid_data else "invalid-data.json"
    try:
        data = load_data_from_file(filepath)
        result = mongo.collection.insert_one(data)
        print(f"✅ Document inserted with _id: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Failed to insert document: {e}")


if __name__ == "__main__":
    # Check if --invalid flag is passed
    use_invalid_data = "--invalid" in sys.argv
    insert_document(with_valid_data=not use_invalid_data)
