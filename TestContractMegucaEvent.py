import random

from Objs.DBManager.DBManager import DBManager
from Objs.DBManager.Defines import *
from Objs.Events.ContractMegucaEvent import ContractMegucaEvent
from Objs.Events.NewContractableMegucaEvent import NewContractableMegucaEvent
from Objs.Meguca.Defines import *
from Objs.Utils.GlobalDefines import *
from Objs.State.State import State

from Objs.MegucaCity.MegucaCity import MegucaCity

fake_city_id = 500
new_city = MegucaCity(fake_city_id)  # city_id = 500

# First let's make a bunch of gucas.
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
        
manager = DBManager(fake_city_id)
manager.CreateTableIfDoesNotExist(MEGUCA_TABLE_FIELDS, table=MEGUCA_TABLE_NAME)
        
new_state = State(manager)

# Select a meguca as the meguca to apply the ContractMeguca Event to (would normally be set by other event)

event_instance = NewContractableMegucaEvent(new_city)
event_instance.Run(new_state)

# Write to db.
new_state.WriteState()

manager.Commit()

recovered_state = State(manager)

event_instance = ContractMegucaEvent(new_city)

print(event_instance.Run(recovered_state))

recovered_state.WriteState()

new_city.WriteCityToDB(manager, forced=True)

manager.Commit()