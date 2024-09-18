from sqlalchemy import or_

from geoalchemy2 import functions

from app.models.satellite_images_table import *
from app.models.geoserver_table        import *

def get_geoserver_config(db_session):
    # For geoserver url
    return db_session.query(GeoserverConfig).all()

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
        SatelliteImages.compressed_file_path
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

    #return db_session_query.all()
    return db_session_query

def get_tables_from_db_schema(DbConn, inspect, schema_name):
    conn, engine = DbConn.connection()
    inspector    = inspect(engine)

    # Get all tables from the schema
    table_names = inspector.get_table_names(schema=schema_name)

    return table_names
