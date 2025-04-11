import sys
import json
import requests

from decouple import config

import mongodb


def replace_type_with_bson_type(schema):
    """
    Recursively replace 'type' with MongoDB-compatible 'bsonType'
    """

    type_mapping = {
        "integer": "int",
        "number": "double",
        "string": "string",
        "boolean": "bool",
        "array": "array",
        "object": "object"
    }

    if isinstance(schema, dict):
        if "type" in schema:
            schema["bsonType"] = type_mapping.get(schema.pop("type"), "string")
        for key, value in schema.items():
            replace_type_with_bson_type(value)

    elif isinstance(schema, list):
        for item in schema:
            replace_type_with_bson_type(item)

    return schema


def convert_to_mongodb_schema(json_schema):
    """
    Convert standard JSON Schema to MongoDB's $jsonSchema format
    """

    type_mapping = {
        "integer": "int",
        "number": "double",
        "string": "string",
        "boolean": "bool",
        "array": "array",
        "object": "object"
    }

    def replace_type_recursive(schema):
        if isinstance(schema, dict):
            # Replace 'type' with 'bsonType'
            if "type" in schema:
                schema["bsonType"] = type_mapping.get(
                    schema.pop("type"), "string"
                )

            # Handle format conversions
            if "format" in schema:
                if schema.get("bsonType") == "string":
                    if schema["format"] == "email":
                        schema["pattern"] = (
                            "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                        )
                    elif schema["format"] == "date":
                        schema["pattern"] = "^\\d{4}-\\d{2}-\\d{2}$"
                schema.pop("format", None)

            # Recurse into all nested dicts and lists
            for key, value in schema.items():
                replace_type_recursive(value)

        elif isinstance(schema, list):
            for item in schema:
                replace_type_recursive(item)

        return schema

    # Build MongoDB schema
    mongodb_schema = {"$jsonSchema": {}}

    # Copy all top-level fields except $schema
    for key, value in json_schema.items():
        if key != "$schema":
            mongodb_schema["$jsonSchema"][key] = value

    # Recursively replace types and adjust formats
    mongodb_schema["$jsonSchema"] = replace_type_recursive(
        mongodb_schema["$jsonSchema"])

    return mongodb_schema


def fetch_schema_from_url(schema_url):
    """
    Fetch JSON schema from a public URL
    """
    try:
        response = requests.get(schema_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching schema from URL: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: The URL does not contain valid JSON")
        return None


def validate_mongodb_schema_structure(mongodb_schema):
    """
    Validate the schema structure meets MongoDB requirements
    """
    if not isinstance(mongodb_schema, dict):
        print("Error: Schema must be a JSON object")
        return False

    if "$jsonSchema" not in mongodb_schema:
        print("Error: Schema must include $jsonSchema property")
        return False

    json_schema = mongodb_schema["$jsonSchema"]
    required_keys = {"properties"}
    if not all(key in json_schema for key in required_keys):
        print("Error: Schema must include bsonType and properties")
        return False

    return True


def apply_schema_to_collection():
    """Apply schema validation to MongoDB collection"""
    try:
        schema_url = config("SCHEMA_URL")

        # Fetch and validate schema
        schema = fetch_schema_from_url(schema_url)
        mongodb_schema = convert_to_mongodb_schema(schema)
        if not validate_mongodb_schema_structure(mongodb_schema):
            return False

        # Create collection if it doesn't exist
        if mongodb.collection_name not in mongodb.db.list_collection_names():
            mongodb.db.create_collection(mongodb.collection_name)

        # Apply schema validation
        mongodb.db.command({
            "collMod": mongodb.collection_name,
            "validator": mongodb_schema,
            "validationLevel": "strict",
            "validationAction": "error"
        })

        print(
            f"✅ Successfully applied schema to collection "
            f"'{mongodb.collection_name}'"
        )
        return True

    except Exception as e:
        print(f"❌ Error applying schema to MongoDB: {e}")
        return False


if __name__ == "__main__":
    print("Starting schema application process...")
    if apply_schema_to_collection():
        print("✅ Schema application completed successfully!")
    else:
        print("❌ Schema application failed")
        sys.exit(1)
