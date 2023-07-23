from sqlalchemy import insert

from app.models.models                 import *
from app.models.satellite_images_table import *
from app.models.geoserver_table        import *

# Check if table exist
def check_table(engine, db_tables, i):
    insp = db.inspect(engine)
    
    if not insp.has_table(i, schema="public"):
        db_tables[i].__table__.create(engine)

# Check database
db_credentials_path = "config/db_geoportal_credentials.csv"
DbConn = DatabaseConfig(db_credentials_path)
DbConn.check_database()

# Check database tables
conn, engine = DbConn.connection()
for i in db_tables:
    check_table(engine, db_tables, i)

# Add geoserver configuration
stmt = insert(GeoserverConfig).values(
    url         = "http://172.18.0.3:8080/geoserver",
    workspace   = "satellite_images",
    service     = "wms",
    format_     = "image/png",
    transparent = True
)
result = conn.execute(stmt)
conn.commit()
conn.close()
