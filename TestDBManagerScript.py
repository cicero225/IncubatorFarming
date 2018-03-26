import random
import sqlite3

from Objs.DBManager.Defines import *
from Objs.Utils.GlobalDefines import *
from Objs.DBManager.DBManager import DBManager
from Objs.Meguca.Defines import *
from Objs.Meguca.Meguca import Meguca
from Objs.MegucaCity.MegucaCity import MegucaCity

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
    
# Test writing and reading a meguca from the DB. This ignores reconstructing friends, etc.

manager.CreateTableIfDoesNotExist(MEGUCA_TABLE_FIELDS, table=MEGUCA_TABLE_NAME)

new_meguca = Meguca.MakeNew()

print("Full Random Meguca:")
print(new_meguca)

print('Writing Meguca to DB...')

meguca_row = new_meguca.ToMegucaRow(fake_city_id)

# One row dict.
write_dict = {frozenset(getattr(meguca_row, x) for x in MEGUCA_PRIMARY_KEYS): (meguca_row, True)}

manager.WriteTable(write_dict, [x[0] for x in MEGUCA_TABLE_FIELDS], table=MEGUCA_TABLE_NAME, forced=True)

manager.Commit()

print('Reading only Meguca From DB...')

# Read rows back.
rows = manager. ReadTable(MEGUCA_ROW, MEGUCA_PRIMARY_KEYS, table=MEGUCA_TABLE_NAME, read_flag="read_only")

same_meguca = Meguca.FromMegucaRow(list(rows.values())[0][0])

print(same_meguca)

assert(new_meguca == same_meguca)


# Make a large city and try writing/reading it too.

# Default in-memory db
manager = DBManager(456)
# Test writing and reading a meguca from the DB. This ignores reconstructing friends, etc.
manager.CreateTableIfDoesNotExist(MEGUCA_TABLE_FIELDS, table=MEGUCA_TABLE_NAME)
new_city = MegucaCity(456)  # city_id = 456

for _ in range(50):
    new_meguca = new_city.NewSensorMeguca()
    # Hardcode just for testing here
    rand_val = random.random()
    if rand_val < 0.25:
        new_city.ContractMeguca(new_meguca.id)
    elif rand_val < 0.5:
        new_city.ContractMeguca(new_meguca.id)
        new_city.WitchMeguca(new_meguca.id)
    elif rand_val < 0.75:
        new_city.KillPotential(new_meguca.id)

new_city.WriteCityToDB(manager, forced=True)

manager.Commit()

city_clone = MegucaCity.ReadCityFromDb(456, manager)
# Necessasry or else these will not compare equal
new_city.original_read_dict = city_clone.original_read_dict

assert(city_clone == new_city)