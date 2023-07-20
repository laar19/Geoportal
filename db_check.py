from app.models.models                 import DatabaseConfig
from app.models.satellite_images_table import *

# Check database
db_credentials_path = "config/db_credentials_geoportal.csv"
DbConn = DatabaseConfig(db_credentials_path)
DbConn.check_database()

# Check database tables
conn, engine = DbConn.connection()
for i in db_tables:
    check_satellite_images_table(engine, db_tables, i)
conn.close()
