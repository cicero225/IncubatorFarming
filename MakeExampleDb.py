import random
import sqlite3

from Objs.DBManager.Defines import *
from Objs.Utils.GlobalDefines import *
from Objs.DBManager.DBManager import DBManager
from Objs.Meguca.Defines import *
from Objs.Meguca.Meguca import Meguca
from Objs.MegucaCity.MegucaCity import MegucaCity

# Make a large city and try writing it.
manager = DBManager(456, db_path="Data\ExampleDb.db")

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