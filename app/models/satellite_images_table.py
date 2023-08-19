from app.models.models import *

table_name = "satellite_images"
class SatelliteImages(Base):
    __tablename__ = table_name
    
    id                      = Column(Integer, primary_key=True, autoincrement=True)
    custom_id               = Column(VARCHAR, unique=True)
    #compressed_file_hash    = Column(VARCHAR, nullable=True)
    satellite               = Column(VARCHAR)
    sensor                  = Column(VARCHAR)
    orbit                   = Column(VARCHAR)
    scene                   = Column(VARCHAR)
    capture_date            = Column(DateTime)
    image_coordinates       = Column(Geometry("POLYGON"), nullable=False)
    cutted_image_shape      = Column(Geometry("POLYGON"))
    #cutted_image_shape    = Column(Geometry('POLYGON', 4326), nullable=False)
    solar_elevation         = Column(FLOAT)
    solar_azimuth           = Column(FLOAT)
    cloud_percentage        = Column(FLOAT)
    solar_irradiance        = Column(FLOAT)
    k_val                   = Column(FLOAT) # K
    b_val                   = Column(FLOAT) # B
    satellite_altitude      = Column(FLOAT)
    zenit_satellite_angle   = Column(FLOAT)
    satellite_azimuth_angle = Column(FLOAT)
    roll_angle              = Column(FLOAT)
    #compressed_name         = Column(VARCHAR)
    rawdatafn               = Column(VARCHAR)
    thumb_path              = Column(VARCHAR)
    geothumb_path           = Column(VARCHAR)
    compressed_file_path    = Column(VARCHAR, nullable=True)
    metadata_xml            = Column(Text)
    create_date             = Column(DateTime, default=dtime.now)
    
db_tables[table_name] = SatelliteImages
