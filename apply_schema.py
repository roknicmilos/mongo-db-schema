import sys
import json
import requests

from pymongo import MongoClient
from decouple import config


def fetch_schema_from_url(schema_url):
    """Fetch JSON schema from a public URL"""
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


def validate_schema_structure(schema):
    """Validate the schema structure meets MongoDB requirements"""
    if not isinstance(schema, dict):
        print("Error: Schema must be a JSON object")
        return False

    if '$jsonSchema' not in schema:
        print("Error: Schema must include $jsonSchema property")
        return False

    json_schema = schema['$jsonSchema']
    required_keys = {'bsonType', 'properties'}
    if not all(key in json_schema for key in required_keys):
        print("Error: Schema must include bsonType and properties")
        return False

    return True


def apply_schema_to_collection():
    """Apply schema validation to MongoDB collection"""
    try:
        # Get configuration from .env
        mongo_uri = config('MONGO_URI')
        db_name = config('DB_NAME')
        collection_name = config('COLLECTION_NAME')
        schema_url = config('SCHEMA_URL')

        # Fetch and validate schema
        schema = fetch_schema_from_url(schema_url)
        if not schema or not validate_schema_structure(schema):
            return False

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]

        # Create collection if it doesn't exist
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)

        # Apply schema validation
        db.command({
            'collMod': collection_name,
            'validator': schema,
            'validationLevel': 'strict',
            'validationAction': 'error'
        })

        print(
            f"✅ Successfully applied schema to collection '{collection_name}'")
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
