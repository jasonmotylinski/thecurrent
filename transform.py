import config
import duckdb
import glob

def init():
    sql = """   
    SET GLOBAL sqlite_all_varchar = true;
    ATTACH 'sqlite:{sqlite_db}' AS sqlite;
    ATTACH 'postgres:dbname={pg_db_name}' AS postgres;
    """.format(**{"sqlite_db": config.DB, "pg_db_name": config.DB_NAME})
    con = duckdb.connect("file.db")
    con.sql(sql)
    return con


def transforms():
    for f in glob.glob('sql/transforms/*.sql', recursive=True):
        with open(f) as sql:
            yield(sql.read())

con = init()

for t in transforms():
    con.sql(t)



