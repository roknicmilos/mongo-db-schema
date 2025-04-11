import json
import sys

import mongodb


def load_data_from_file(file_path: str) -> dict | list:
    """
    Load JSON data from file, handling both single objects and lists.
    """

    with open(file_path, "r") as f:
        data = json.load(f)

        if isinstance(data, (dict, list)):
            return data
        raise ValueError(
            "JSON data should be either an object or an array of objects"
        )


def insert_data(data: dict | list) -> None:
    """
    Insert data into MongoDB, handling both single documents
    and bulk (list) inserts.
    """

    if not data:
        raise ValueError("⚠️ No data to insert")

    try:
        if isinstance(data, dict):
            # Single document insertion
            result = mongodb.collection.insert_one(data)
            print(f"✅ Inserted 1 document with _id: {result.inserted_id}")
        else:
            # Multiple documents insertion
            result = mongodb.collection.insert_many(data)
            print(f"✅ Inserted {len(result.inserted_ids)} documents")
            print(f"First document ID: {result.inserted_ids[0]}")

    except Exception as e:
        print(f"❌ Failed to insert data: {e}")
        # Consider adding more specific exception handling here


def main() -> None:
    """Main execution flow with flexible file input."""
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename.json>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        data = load_data_from_file(filename)
        insert_data(data)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in file: {filename}")
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
    except ValueError as ve:
        print(f"❌ Data validation error: {ve}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
