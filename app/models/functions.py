from sqlalchemy import or_

from geoalchemy2 import functions

from app.models.satellite_images_table import *
from app.models.geoserver_table        import *

def intersect(db_session, filters):
    db_session_query = db_session.query(
        # For geoserver url
        GeoserverConfig.url,
        GeoserverConfig.workspace,
        GeoserverConfig.service,
        GeoserverConfig.format_,
        GeoserverConfig.transparent,
        SatelliteImages.custom_id,
        
        # Satellite info
        SatelliteImages.satellite,
        SatelliteImages.sensor,
        SatelliteImages.orbit,
        SatelliteImages.escene,
        SatelliteImages.capture_date,
        #functions.ST_AsText(SatelliteImages.cutted_image_shape),
        functions.ST_AsGeoJSON(SatelliteImages.cutted_image_shape),
        SatelliteImages.solar_elevation,
        SatelliteImages.solar_azimuth,
        SatelliteImages.cloud_percentage,
        SatelliteImages.solar_irradiance,
        SatelliteImages.k_val,
        SatelliteImages.b_val,
        SatelliteImages.satellite_altitude,
        SatelliteImages.zenit_satellite_angle,
        SatelliteImages.satellite_azimuth_angle,
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
            SatelliteImages.escene==filters["scene"]
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
                int(filters["roll_angle"])*-1, int(filters["roll_angle"])
            )
        )

    """
    if filters["roll_angle"]:
        db_session_query = db_session_query.where(
            SatelliteImages.roll_angle>=filters["roll_angle"]
        )
    """

    #return db_session_query.all()
    return db_session_query
