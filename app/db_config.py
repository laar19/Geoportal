import sqlalchemy as db
import pandas     as pd

class DbConnection:
    def get_credentials(self, path, position):
        credentials = pd.read_csv(path)

        db_credentials = {}

        db_credentials["database"] = credentials["database"][position]
        db_credentials["host"]     = credentials["host"][position]
        db_credentials["db_name"]  = credentials["db_name"][position]
        db_credentials["user"]     = credentials["user"][position]
        db_credentials["password"] = credentials["password"][position]

        return db_credentials

    def connection(self, path, position):
        credentials = self.get_credentials(path, position)
        database    = credentials["database"]
        host        = credentials["host"]
        db_name     = credentials["db_name"]
        user        = credentials["user"]
        password    = credentials["password"]
        
        engine = db.create_engine(f"{database}://{user}:{password}@{host}/{db_name}")
        conn   = engine.connect()

        return conn, engine

    def select_table(self, table_name, conn, engine):
        metadata = db.MetaData()
        table    = db.Table(table_name, metadata, autoload=True, autoload_with=engine)
        query    = table.select()

        return query
