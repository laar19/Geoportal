import pandas as pd

from datetime import datetime

from sqlalchemy       import Column, MetaData, create_engine, schema, Table
from sqlalchemy.types import *
from sqlalchemy.orm   import registry, declarative_base, Session, sessionmaker

from sqlalchemy_utils import create_database, database_exists

from geoalchemy2 import Geometry

#######################################################################
# Start DB set up
class DBConfig:
    def __init__(self, path, position=0):
        self.path     = path
        self.position = position
        
    def get_credentials(self):
        credentials = pd.read_csv(self.path)

        # Credentials
        c = {}

        c["database"] = credentials["database"][self.position]
        c["host"]     = credentials["host"][self.position]
        c["db_name"]  = credentials["db_name"][self.position]
        c["user"]     = credentials["user"][self.position]
        c["password"] = credentials["password"][self.position]

        target_db_uri = f"{c['database']}://{c['user']}:{c['password']}@{c['host']}/{c['db_name']}"
        #main_db_uri   = f"{c['database']}://{c['user']}:{c['password']}@{c['host']}"

        #return main_db_uri, target_db_uri
        return target_db_uri

    def connection(self):
        # Credentials
        #main_db_uri, target_db_uri = self.get_credentials()
        target_db_uri = self.get_credentials()
        
        engine = create_engine(target_db_uri)
        conn   = engine.connect()

        return conn, engine

    """
    def select_table(self, table_name, engine):
        metadata = db.MetaData()
        table    = db.Table(table_name, metadata, autoload=True, autoload_with=engine)
        query    = table.select()

        return query
    """

    # Create DB if doesn't exist
    def check_database(self):
        # Credentials
        #main_db_uri, target_db_uri = self.get_credentials()
        target_db_uri = self.get_credentials()
        
        if not database_exists(target_db_uri):
            create_database(target_db_uri)
            
            conn, engine = self.connection()
            
            """
            statement = text("""'CREATE EXTENSION postgis'""")
            for line in data:
                con.execute(statement, **line)
            """
            conn.execute("CREATE EXTENSION postgis")
            
            schema_name = "satellite_images"

            if not engine.dialect.has_schema(engine, schema_name):
                engine.execute(schema.CreateSchema(schema_name))
                conn.close()
                
                return False
# End DB set up
#######################################################################

#######################################################################
# Tables
DBConfig = DBConfig("db_credentials.csv")

if not DBConfig.check_database():
    conn, engine = DBConfig.connection()
    
    Base = declarative_base()

    #metadata = MetaData(bind=engine)

    class Image(Base):
        __tablename__  = "images"
        __table_args__ = {"schema": "satellite_images"}
        #__abstract__   = True

        id                 = Column(Integer, primary_key=True, autoincrement=True)
        date               = Column(DateTime)
        satellite          = Column(String)
        sensor             = Column(String)
        image_coordinates  = Column(Geometry("POLYGON"), nullable=False)
        cutted_image_shape = Column(Geometry("POLYGON"))
        #cutted_image_shape = Column(Geometry('POLYGON', 4326), nullable=False)
        path               = Column(String)
        metadata_xml       = Column(Text)
        create_date        = Column(DateTime, default=datetime.now)
        
        def __init__(self, date=None, satellite=None, sensor=None, image_coordinates=None, cutted_image_shape=None,
                     path=None, metadata_xml=None, create_date=None):
            self.date               = date 
            self.satellite          = satellite 
            self.sensor             = sensor
            self.image_coordinates  = image_coordinates
            self.cutted_image_shape = cutted_image_shape
            self.path               = path
            self.metadata_xml       = metadata_xml
            self.create_date        = create_date
            
        #query = cars.insert().values(make="Kia", model="Telluride", year="2021")
        #connection.execute(query)
        """
        insert_query = users.insert().values([
            {"first_name": "Bob", "last_name": "Jones", "email_address": "bjones@notrealemail.com"},
            {"first_name": "Jack", "last_name": "Erich", "email_address": "jerich@notrealemail.com"},
            {"first_name": "Rick", "last_name": "Stein", "email_address": "rstein@notrealemail.com"},
            {"first_name": "Sally", "last_name": "Green", "email_address": "sgreen@notrealemail.com"}
        ])
        connection.execute(insert_query)
        """
        """
        from sqlalchemy import insert
        stmt = (
            insert(user_table).
            values(name='username', fullname='Full Username')
        )
        """
            
        def create(self, session):
            new_image = Image(self.date, self.satellite, self.sensor, self.image_coordinates,
                              self.cutted_image_shape, self.path, self.metadata_xml, self.create_date)
            
            session.add(new_image)
            session.commit()
            session.close()
            
        def read(self, session):
            # SELECT COUNT(*) FROM Actor
            result = session.query(Image).count()
            
            #from sqlalchemy import select
            #stmt = select(User).where(User.name == 'spongebob')
            #result = session.execute(select(User).order_by(User.id))
            #result = session.execute(stmt)
            #result.scalars().all()
            """
            result = session.execute(
                select(User.name, Address.email_address).
                join(User.addresses).
                order_by(User.id, Address.id))
            """

    #SateliteImages.__table__.create(engine)
    #metadata.create_all()
    Base.metadata.create_all(engine)
    conn.close()
# End Tables
#######################################################################
