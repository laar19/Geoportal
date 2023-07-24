from geoalchemy2 import functions

from app.models.satellite_images_table import *
from app.models.geoserver_table        import *

def intersect(db_session, polygon):
    return db_session.query(
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
    ).filter(
        func.ST_Intersects(SatelliteImages.cutted_image_shape, from_shape(polygon))
    ).all()
