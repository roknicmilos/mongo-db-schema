# MongoDB Schema Manager Tool

A simple tool for applying and testing JSON schema validation in MongoDB
collections.

---

## 🚀 What Can This Tool Do?

- **Apply a standard JSON Schema** to a MongoDB collection  
  Loads a schema from a given URL, converts it to MongoDB’s `$jsonSchema`
  format, and applies it to the target collection.

- **Test schema validation**  
  Insert valid or intentionally invalid data to verify the schema enforcement in
  MongoDB.

---

## ⚙️ Setup

1. Clone the repository:

   ```bash
   git clone git@github.com:roknicmilos/mongo-db-schema.git
   ```

2. Change directory to the project folder:

   ```bash
   cd mongo-db-schema
   ```

3. (Optional) Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   ```

    - On Windows:
       ```bash
       .venv\Scripts\activate
       ```
    - On macOS/Linux:
       ```bash
       source .venv/bin/activate
       ```

4. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
5. Create `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   ```
    - Update `.env` with your MongoDB connection string, database name, and
      schema
      URL.

## Available scripts:

- Apply schema to MongoDB collection:

  ```bash
  python apply_schema.py
  ```

- Test applied schema by inserting **valid data** into the specified collection:

  ```bash
  python insert_data.py
  ```

- Test applied schema by inserting **invalid data** into the specified
  collection:

  ```bash
  python insert_data.py --invalid
  ```
