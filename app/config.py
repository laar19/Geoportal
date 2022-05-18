import sqlalchemy as db

import pandas as pd

import datetime

from werkzeug.security import generate_password_hash

from sqlalchemy_utils import create_database, database_exists

SECRET_KEY = generate_password_hash(str(datetime.datetime.now()))

#######################################################################
# Begin map config

proj_4326 = 4326
#proj_3857 = 3857
main_projection = proj_4326;

class MapDiv:
    def main_config(self):
        center = [-65.89003678746177, 8.016859315038008]
        zoom   = 5.5

        return {"center": center, "zoom": zoom}
        
# End map config
#######################################################################

#######################################################################
# Begin DB config

class DBConfig:
    def get_credentials(self, path, position):
        credentials = pd.read_csv(path)

        # Credentials
        c = {}

        c["database"] = credentials["database"][position]
        c["host"]     = credentials["host"][position]
        c["db_name"]  = credentials["db_name"][position]
        c["user"]     = credentials["user"][position]
        c["password"] = credentials["password"][position]

        db_uri = f"{c['database']}://{c['user']}:{c['password']}@{c['host']}/{c['db_name']}"

        return db_uri

    def connection(self, path, position):
        # Credentials
        db_uri = self.get_credentials(path, position)
        
        engine = db.create_engine(db_uri)
        conn   = engine.connect()

        return conn, engine

    def select_table(self, table_name, engine):
        metadata = db.MetaData()
        table    = db.Table(table_name, metadata, autoload=True, autoload_with=engine)
        query    = table.select()

        return query

    def check_database(self, path, position):
        # Credentials
        db_uri = self.get_credentials(path, position)
        
        if not database_exists(db_uri):
            create_database(db_uri)

            if not engine.dialect.has_schema(engine, schema_name):
                engine.execute(sqlalchemy.schema.CreateSchema(schema_name))

        return False

# End DB config
#######################################################################
