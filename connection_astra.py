from astrapy import DataAPIClient
# Initialize the client
client = DataAPIClient("AstraCS:PPCvvAAEjbgzUQYyYXfCFwDW:7462eb2e1ec92ce27fb4652468d6cdd0a8087e5c4c762591cff633daf70610b2")
db = client.get_database_by_api_endpoint(
  "https://f797bcb2-c37b-4e3e-bc4a-911e364b5b01-us-east-2.apps.astra.datastax.com"
)
print(f"Connected to Astra DB: {db.list_collection_names()}")
