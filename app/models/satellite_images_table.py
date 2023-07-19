from datetime import datetime

import sqlalchemy as db
from sqlalchemy       import Column, func
from sqlalchemy.types import *
from sqlalchemy.orm   import declarative_base

from geoalchemy2       import Geometry
from geoalchemy2.shape import from_shape

db_tables = []

"""
Base = declarative_base()
table_name = "satellite_images"
class SatelliteImages(Base):
    __tablename__ = table_name
    
    id                    = Column(Integer, primary_key=True, autoincrement=True)
    satelliteid           = Column(VARCHAR)
    sensorid              = Column(VARCHAR)
    #sensorId              = Column(String)
    productdate           = Column(DateTime)
    image_coordinates     = Column(Geometry("POLYGON"), nullable=False)
    cutted_image_shape    = Column(Geometry("POLYGON"))
    #cutted_image_shape    = Column(Geometry('POLYGON', 4326), nullable=False)
    path                  = Column(String)
    metadata_xml          = Column(Text)
    productupperleftlat   = Column(VARCHAR)
    productupperleftlong  = Column(VARCHAR)
    productupperrightlat  = Column(VARCHAR)
    productupperrightlong = Column(VARCHAR)
    productlowerleftlat   = Column(VARCHAR)
    productlowerleftlong  = Column(VARCHAR)
    productlowerrightlat  = Column(VARCHAR)
    productlowerrightlong = Column(VARCHAR)
    dataupperleftlat      = Column(VARCHAR)
    dataupperleftlong     = Column(VARCHAR)
    dataupperrightlat     = Column(VARCHAR)
    dataupperrightlong    = Column(VARCHAR)
    datalowerleftlat      = Column(VARCHAR)
    datalowerleftlong     = Column(VARCHAR)
    datalowerrightlat     = Column(VARCHAR)
    datalowerrightlong    = Column(VARCHAR)
    create_date           = Column(DateTime, default=datetime.now)
"""

Base = declarative_base()
table_name = "satellite_images"
db_tables.append(table_name)
class SatelliteImages(Base):
    __tablename__ = table_name
    
    id                         = Column(Integer, primary_key=True, autoincrement=True)
    compressed_file_hash       = Column(VARCHAR, nullable=True)
    #id_hashed                  = Column(String)
    satellite                  = Column(VARCHAR)
    sensor                     = Column(VARCHAR)
    orbit                      = Column(VARCHAR)
    escene                     = Column(VARCHAR)
    capture_date               = Column(DateTime)
    image_coordinates          = Column(Geometry("POLYGON"), nullable=False)
    cutted_image_shape         = Column(Geometry("POLYGON"))
    #cutted_image_shape    = Column(Geometry('POLYGON', 4326), nullable=False)
    solar_elevation            = Column(VARCHAR)
    solar_azimuth              = Column(VARCHAR)
    cloud_percentage           = Column(VARCHAR)
    solar_irradiance           = Column(VARCHAR)
    K                          = Column(VARCHAR)
    B                          = Column(VARCHAR)
    satellite_altitude         = Column(VARCHAR)
    zenit_satellite_angle      = Column(VARCHAR)
    satellite_azimuth_angle    = Column(VARCHAR)
    angulo_roll                = Column(VARCHAR)
    compressed_name            = Column(VARCHAR)
    rawdatafn                  = Column(VARCHAR)
    thumb_path                 = Column(VARCHAR)
    geothumb_path              = Column(VARCHAR)
    geoserver_url_html_preview = Column(VARCHAR)
    geoserver_url_map_preview  = Column(VARCHAR)
    metadata_xml               = Column(Text, nullable=True)
    compressed_file_path       = Column(VARCHAR, nullable=True)
    create_date                = Column(DateTime, default=datetime.now)

def intersect(db_session, polygon):
    return db_session.query(
        SatelliteImages.geoserver_url_html_preview,
        SatelliteImages.geoserver_url_map_preview
    ).filter(
        func.ST_Intersects(SatelliteImages.cutted_image_shape, from_shape(polygon))
    ).all()

# Check if table exist
def check_satellite_images_table(engine, table_name):
    insp = db.inspect(engine)
    
    if not insp.has_table(table_name, schema="public"):
        SatelliteImages.__table__.create(engine)
