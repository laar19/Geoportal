from app.models.satellite_images_table import *
from app.models.geoserver_table        import *

def intersect(db_session, polygon):
    return db_session.query(
        GeoserverConfig.url,
        GeoserverConfig.workspace,
        GeoserverConfig.service,
        GeoserverConfig.format_,
        GeoserverConfig.transparent,
        SatelliteImages.custom_id,
    ).filter(
        func.ST_Intersects(SatelliteImages.cutted_image_shape, from_shape(polygon))
    ).all()
