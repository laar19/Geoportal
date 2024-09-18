# Import the library
from geo.Geoserver import Geoserver

from sqlalchemy import create_engine, inspect

# DB connection
db_type  = "postgresql"
host     = "localhost"
port     = "8870"
db_name  = "geoportal_db"
user     = "root"
password = "root"

engine = create_engine(f"{db_type}://{user}:{password}@{host}:{port}/{db_name}")

inspector = inspect(engine)

# Get all tables from the schema
schema_name = "test"
table_names = inspector.get_table_names(schema=schema_name)
print(table_names)

# Initialize the library
geo = Geoserver("http://localhost:8873/geoserver", username="root", password="root")

# For creating workspace
for i in table_names:    
    try:
        geo.create_workspace(workspace=workspace)
    except Exception as e:
        if "409" in str(e):
            print("Workspace already exist")
            print("Continue...")
    finally:
        # For creating postGIS connection and publish postGIS table
        geo.create_featurestore(
            store_name  = i,
            workspace   = i,
            db          = "geoportal_db",
            host        = "172.22.0.1", # docker gateway
            port        = "8870",
            schema      = schema_name,
            pg_user     = "root",
            pg_password = "root"
        )

        geo.publish_featurestore(
            workspace  = i,
            store_name = i,
            pg_table   = i
        )
