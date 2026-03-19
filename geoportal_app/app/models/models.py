import sys

import pandas as pd

import sqlalchemy as db
from sqlalchemy       import MetaData, create_engine, Column, func
from sqlalchemy.orm   import declarative_base
from sqlalchemy.types import *

from sqlalchemy_utils import database_exists

from geoalchemy2       import Geometry
from geoalchemy2.shape import from_shape

from datetime import datetime as dtime

Base = declarative_base()

db_tables = {}

class DatabaseConfig:
    def __init__(self, db, db_user, db_password, db_host, db_port, db_name):
        self.db          = db
        self.db_user     = db_user
        self.db_password = db_password
        self.db_host     = db_host
        self.db_port     = db_port
        self.db_name     = db_name
        
    def get_credentials(self):
        #target_db_uri = f"{self.db}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        target_db_uri = "{}://{}:{}@{}:{}/{}".format(
            self.db,
            self.db_user,
            self.db_password,
            self.db_host,
            self.db_port,
            self.db_name
        )

        #return main_db_uri, target_db_uri
        return target_db_uri

    def connection(self):
        # Credentials
        #main_db_uri, target_db_uri = self.get_credentials()
        target_db_uri = self.get_credentials()
        
        engine = create_engine(target_db_uri)
        conn   = engine.connect()

        return conn, engine

    def select_table(self, table_name, engine):
        metadata = db.MetaData()
        #table    = db.Table(table_name, metadata, autoload=True, autoload_with=engine)
        table    = db.Table(table_name, metadata, autoload_with=engine)
        query    = table.select()

        return query

    # Create DB if doesn't exist
    def check_database(self):
        target_db_uri = self.get_credentials()
        
        if not database_exists(target_db_uri):
            print("\n\nCAN'T CONNECT TO DATABASE\nCHECK DATABASE STATUS")
            sys.exit()
