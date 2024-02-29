import config
import duckdb
import glob
import sys

TRANFORMS_ROOT="sql/transforms/"

def init():
    data={"sqlite_db": config.DB, 
          "db_pg_name": config.DB_NAME, 
          "db_pg_user": config.DB_PG_USER,
          "db_pg_passwd": config.DB_PG_PASSWD,
          "db_pg_host": config.DB_PG_HOST
          }
    sql = """   
    SET GLOBAL sqlite_all_varchar = true;
    ATTACH 'sqlite:{sqlite_db}' AS sqlite;
    ATTACH 'postgres:dbname={db_pg_name} user={db_pg_user} password={db_pg_passwd} host={db_pg_host}' AS postgres;
    """.format(**data)
    con = duckdb.connect("file.db")
    con.sql(sql)
    return con

def transforms():
    for f in glob.glob('{0}*.sql'.format(TRANFORMS_ROOT), recursive=True):
        with open(f) as sql:
            yield(sql.read())

if __name__=="__main__": 
    con = init()

    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            with open(TRANFORMS_ROOT + a) as sql:
                con.sql(sql.read())
    else:
        for t in transforms():
            con.sql(t)



