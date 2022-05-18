from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Column, MetaData
from sqlalchemy.types           import *

from geoalchemy2 import Geometry

Base = declarative_base()

metadata = MetaData(bind=engine)
metadata.create_all()

tables = list()

class SateliteImages(Base):
    __tablename__ = "satellite_images"
    __table__ = Table("users", metadata, autoload=True)
    
    id                 = Column(Integer, primary_key=True)
    date               = Column(DateTime)
    satellite          = Column(String)
    sensor             = Column(String)
    image_coordinates  = Column(Geometry('POLYGON'))
    cutted_image_shape = Column(Geometry('POLYGON'))
    path               = Column(String)
    metadata           = Column(Text)
    create_date        = Column(DateTime, default=datetime.now)
