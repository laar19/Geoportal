from app.models.models import *

table_name = "geoserver_config"
class GeoserverConfig(Base):
    __tablename__ = table_name
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    url         = Column(VARCHAR)
    workspace   = Column(VARCHAR)
    service     = Column(VARCHAR)
    format_     = Column(VARCHAR)
    transparent = Column(VARCHAR)
    create_date = Column(DateTime, default=dtime.now)
    
db_tables[table_name] = GeoserverConfig
