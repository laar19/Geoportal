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
        c["port"]     = credentials["port"][self.position]

        target_db_uri = f"{c['database']}://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['db_name']}"
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
