import peewee as pw

from chatpilot.config import DB_PATH

DB = pw.SqliteDatabase(DB_PATH)
DB.connect()
