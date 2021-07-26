"""
from sqlalchemy import create_engine, select, Table, MetaData
from sqlalchemy.sql import text
"""

import sqlalchemy as db

import pandas as pd
#import geopandas as gpd

class DbConnection:
    def get_credentials(self, path):
        credentials = pd.read_csv(path)

        db_credentials = {}

        db_credentials["database"] = credentials["database"][0]
        db_credentials["host"]     = credentials["host"][0]
        db_credentials["db_name"]  = credentials["db_name"][0]
        db_credentials["user"]     = credentials["user"][0]
        db_credentials["password"] = credentials["password"][0]

        return db_credentials

    def connection(self, path):
        credentials = self.get_credentials(path)
        database    = credentials["database"]
        host        = credentials["host"]
        db_name     = credentials["db_name"]
        user        = credentials["user"]
        password    = credentials["password"]
        
        #connection = f"postgresql://{user}:{password}@{host}/{database}"
        #engine     = create_engine(connection)        
        engine = db.create_engine(f"{database}://{user}:{password}@{host}/{db_name}")
        conn   = engine.connect()

        return conn, engine

    def select_table(self, table_name, conn, engine):
        #s = select([table])
        #s = select(text(table))
        #r = conn.execute(s)

        """
        table = Table(table_name, MetaData(), autoload_with=conn)
        query = table.select()
        #r = engine.execute(query)
        result = conn.execute(query)
        """

        metadata = db.MetaData()
        table    = db.Table(table_name, metadata, autoload=True, autoload_with=engine)
        query    = table.select()
        #result   = conn.execute(query)

        #result = gpd.read_postgis(sql=query, con=conn).to_json()
        #result = pd.read_sql(query, conn)

        #return result
        return query
