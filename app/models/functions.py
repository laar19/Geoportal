from sqlalchemy import or_

from geoalchemy2 import functions

from app.models.satellite_images_table import *
from app.models.vectors_table          import *
from app.models.geoserver_table        import *

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from shapely.geometry import Polygon
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy import create_engine, inspect
from sqlalchemy import create_engine, MetaData, Table

def get_tables_from_db_schema(DbConn, inspect, schema_name):
    conn, engine = DbConn.connection()
    inspector    = inspect(engine)

    # Get all tables from the schema
    table_names = inspector.get_table_names(schema=schema_name)

    return table_names

def get_geoserver_config(db_session):
    # For geoserver url
    return db_session.query(GeoserverConfig).all()

"""
def intersect(db_session, filters):
    # Satellite info
    db_session_query = db_session.query(
        SatelliteImages.custom_id,
        SatelliteImages.satellite,
        SatelliteImages.sensor,
        SatelliteImages.orbit,
        SatelliteImages.scene,
        SatelliteImages.capture_date,
        #functions.ST_AsText(SatelliteImages.cutted_image_shape),
        functions.ST_AsGeoJSON(SatelliteImages.cutted_image_shape),
        SatelliteImages.cloud_percentage,
        SatelliteImages.roll_angle,
        SatelliteImages.compressed_file_path,
        SatelliteImages.geoserver_workspace,
        SatelliteImages.geoserver_service,
        SatelliteImages.geoserver_format,
        SatelliteImages.geoserver_transparent
    )

    if filters["coordinates"]:
        db_session_query = db_session_query.filter(
            func.ST_Intersects(
                SatelliteImages.cutted_image_shape,
                from_shape(filters["coordinates"])
            )
        )

    if filters["satellite"]:
        db_session_query = db_session_query.where(
            SatelliteImages.satellite==filters["satellite"]
        )
        
    if filters["sensor_pan"] and filters["sensor_mss"]:
        db_session_query = db_session_query.filter(
            or_(
                SatelliteImages.sensor == filters["sensor_pan"],
                SatelliteImages.sensor == filters["sensor_mss"]
            )
        )
    else:
        if filters["sensor_pan"]:
            db_session_query = db_session_query.where(
                SatelliteImages.sensor==filters["sensor_pan"]
            )
        if filters["sensor_mss"]:
            db_session_query = db_session_query.where(
                SatelliteImages.sensor==filters["sensor_mss"]
            )

    if filters["orbit"]:
        db_session_query = db_session_query.where(
            SatelliteImages.orbit==filters["orbit"]
        )
        
    if filters["scene"]:
        db_session_query = db_session_query.where(
            SatelliteImages.scene==filters["scene"]
        )

    if filters["start_date"] and filters["end_date"]:
        db_session_query = db_session_query.filter(
            SatelliteImages.capture_date.between(
                filters["start_date"], filters["end_date"]
            )
        )

    if filters["roll_angle"]:
        db_session_query = db_session_query.where(
            SatelliteImages.roll_angle.between(
                float(filters["roll_angle"])*-1, float(filters["roll_angle"])
            )
        )
        
    if filters["cloud_percentage"]:
        db_session_query = db_session_query.where(
            SatelliteImages.cloud_percentage.between(
                float(0), float(filters["cloud_percentage"])
            )
        )

    return db_session_query
"""
    
def intersect(db_session, filters, engine):
    # Create an inspector object
    inspector = inspect(engine)

    # Specify the schema name
    schema_name = "vectors"

    # Get all table names in the specified schema
    table_names = inspector.get_table_names(schema=schema_name)

    for i in table_names:
        # Reflect the existing table
        metadata = MetaData()

        table = Table(i, metadata, schema="vectors", autoload_with=engine)

        # Query the table
        db_session_query = db_session.query(
            table.custom_id,
            table.name,
            table.geoserver_workspace,
            table.geoserver_service,
            table.geoserver_format,
            table.geoserver_transparent
        )#.filter(example_table.c.value > 1).all()

    """
    if filters["coordinates"]:
        db_session_query = db_session_query.filter(
            func.ST_Intersects(
                Vectors.cutted_image_shape,
                from_shape(filters["coordinates"])
            )
        )
    """

    """
    # Reflect the custom schema table
    metadata = MetaData(schema='vectors')
    your_table = Table('kesPolygon', metadata, autoload_with=engine)

    polygon = Polygon(polygon_coords_4326)

    polygon_wkt = WKTElement(polygon.wkt, srid=4326)

    # Perform the intersection query
    intersect_query = session.query(your_table).filter(
        your_table.c.geometry.ST_Intersects(polygon_wkt)
    )

    # Fetch and print the results
    results = intersect_query.all()
    for result in results:
        print(result)
    """

    return db_session_query
