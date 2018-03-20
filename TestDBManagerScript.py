from Objs.DBManager.Defines import *
from Objs.Utils.GlobalDefines import *
import sqlite3

from Objs.DBManager.DBManager import DBManager

fake_city_id = 500

# Default in-memory db
manager = DBManager(fake_city_id)

# Write an exception
manager.WriteExceptionState("Test Exception")

# Check db explicitly without using object.
c = manager.connection.cursor()
rows = c.execute("SELECT * FROM {}".format(EXCEPTION_TABLE_NAME))

# print columns
print([x[0] for x in c.description])

# print rows
for row in rows:
    print(row)