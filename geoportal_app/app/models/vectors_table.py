from app.models.models import *

table_name = "vectors"
class Vectors(Base):
    __tablename__ = table_name
    
    id                    = Column(Integer, primary_key=True, autoincrement=True)
    custom_id             = Column(VARCHAR, unique=True)
    name                  = Column(VARCHAR)
    geoserver_workspace   = Column(VARCHAR) # Geoserver WMS configuration
    geoserver_service     = Column(VARCHAR) # Geoserver WMS configuration
    geoserver_format      = Column(VARCHAR) # Geoserver WMS configuration
    geoserver_transparent = Column(VARCHAR) # Geoserver WMS configuration
    create_date           = Column(DateTime, default=dtime.now)
    
#db_tables[table_name] = Vectors
