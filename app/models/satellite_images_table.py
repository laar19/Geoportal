from app.models.models import *

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
    create_date                = Column(DateTime, default=dtime.now)
    
db_tables[table_name] = SatelliteImages
