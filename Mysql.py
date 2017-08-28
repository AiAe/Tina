import json, pymysql

with open("config.json", "r") as f:
    config = json.load(f)

def connect():
    connection = pymysql.connect(host=config["host"], user=config["user"], passwd=config["pass"], db=config["db"], charset='utf8')
    connection.autocommit(True)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    return connection, cursor

def execute(connection, cursor, sql, args=None):
    try:
        cursor.execute(sql, args) if args is not None else cursor.execute(sql)
        return cursor
    except pymysql.err.OperationalError:
        print ("Something went wrong with mysql connection.... trying to reconnect.")
        connection.connect()
        return execute(sql, args)