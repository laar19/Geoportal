from sqlalchemy import MetaData, Table, inspect, func

#from app.models.satellite_images_table import *
#from app.models.vectors_table          import *
from app.models.geoserver_table        import *

def get_tables_from_db_schema(DbConn, inspect, schema_name):
    conn, engine = DbConn.connection()
    inspector    = inspect(engine)

    # Get all tables from the schema
    table_names = inspector.get_table_names(schema=schema_name)

    return table_names

def get_geoserver_config(db_session):
    # For geoserver url
    return db_session.query(GeoserverConfig).all()

def intersect(db_session, filters, engine):
    # Reflect the existing table
    metadata = MetaData()
    
    # Create an inspector object
    inspector = inspect(engine)

    # Specify the schema name
    schema_name = "vectors"

    # Get all table names in the specified schema
    table_names = inspector.get_table_names(schema=schema_name)

    db_session_query = []
    for i in table_names:
        # Map the table
        table = Table(i, metadata, schema="vectors", autoload_with=engine)

        # Query the table
        result = db_session.query(
            table.c.custom_id,
            table.c.name,
            table.c.geoserver_workspace,
            table.c.geoserver_service,
            table.c.geoserver_format,
            table.c.geoserver_transparent
        )

        # Filter by coordinates
        if filters["coordinates"]:
            polygon_wkt = filters["coordinates"].wkt
            
            # Create a polygon from the WKT
            polygon_geom = func.ST_GeomFromText(polygon_wkt, 4326)

            # Query the table to find intersecting geometries
            result = result.filter(
                table.c.geometry.ST_Intersects(polygon_geom)
            )#.all()

        db_session_query.append(result)

    # Combine the queries of all tables of the schema and automatically
    # remove duplicates
    try:
        combined_query = db_session_query[0]
        for i in db_session_query[1:]:
            combined_query = combined_query.union(i)
        return combined_query
    except Exception as e:
        print("Error:", str(e))
        return False