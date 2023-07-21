from datetime import datetime

import sqlalchemy as db
from sqlalchemy       import Column, func
from sqlalchemy.types import *
from sqlalchemy.orm   import declarative_base

from geoalchemy2       import Geometry
from geoalchemy2.shape import from_shape

Base = declarative_base()

db_tables = {}

table_name = "satellite_images"
class SatelliteImages(Base):
    __tablename__ = table_name
    
    id                         = Column(Integer, primary_key=True, autoincrement=True)
    custom_id                  = Column(VARCHAR, unique=True)
    #compressed_file_hash       = Column(VARCHAR, nullable=True)
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
    k_val                      = Column(VARCHAR) # K
    b_val                      = Column(VARCHAR) # B
    satellite_altitude         = Column(VARCHAR)
    zenit_satellite_angle      = Column(VARCHAR)
    satellite_azimuth_angle    = Column(VARCHAR)
    roll_angle                 = Column(VARCHAR)
    compressed_name            = Column(VARCHAR)
    rawdatafn                  = Column(VARCHAR)
    thumb_path                 = Column(VARCHAR)
    geothumb_path              = Column(VARCHAR)
    compressed_file_path       = Column(VARCHAR, nullable=True)
    metadata_xml               = Column(Text)
    create_date                = Column(DateTime, default=datetime.now)
db_tables[table_name] = SatelliteImages

table_name = "geoserver_config"
class GeoserverConfig(Base):
    __tablename__ = table_name
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    url         = Column(VARCHAR)
    workspace   = Column(VARCHAR)
    service     = Column(VARCHAR)
    format_     = Column(VARCHAR)
    transparent = Column(VARCHAR)
    create_date = Column(DateTime, default=datetime.now)
db_tables[table_name] = GeoserverConfig

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

# Check if table exist
"""
def check_satellite_images_table(engine, table_name):
    insp = db.inspect(engine)
    
    if not insp.has_table(table_name, schema="public"):
        SatelliteImages.__table__.create(engine)
"""
def check_satellite_images_table(engine, db_tables, i):
    insp = db.inspect(engine)
    
    if not insp.has_table(i, schema="public"):
        db_tables[i].__table__.create(engine)
