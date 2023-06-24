from datetime import datetime

import sqlalchemy as db
from sqlalchemy       import Column, func
from sqlalchemy.types import *
from sqlalchemy.orm   import declarative_base

from geoalchemy2       import Geometry
from geoalchemy2.shape import from_shape

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

def intersect(db_session, polygon):
    return db_session.query(
        SatelliteImages.path,
        SatelliteImages.productupperleftlat,
        SatelliteImages.productupperleftlong,
        SatelliteImages.productupperrightlat,
        SatelliteImages.productupperrightlong,
        SatelliteImages.productlowerleftlat,
        SatelliteImages.productlowerleftlong,
        SatelliteImages.productlowerrightlat,
        SatelliteImages.productlowerrightlong,
        SatelliteImages.dataupperleftlat,
        SatelliteImages.dataupperleftlong,
        SatelliteImages.dataupperrightlat,
        SatelliteImages.dataupperrightlong,
        SatelliteImages.datalowerleftlat,
        SatelliteImages.datalowerleftlong,
        SatelliteImages.datalowerrightlat,
        SatelliteImages.datalowerrightlong,
    ).filter(
        func.ST_Intersects(SatelliteImages.cutted_image_shape, from_shape(polygon))
    ).all()

# Check if table exist
def check_satellite_images_table(engine):
    insp = db.inspect(engine)
    
    if not insp.has_table(table_name, schema="public"):
        SatelliteImages.__table__.create(engine)
