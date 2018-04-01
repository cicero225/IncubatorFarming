import random

from Objs.DBManager.DBManager import DBManager
from Objs.DBManager.Defines import *
from Objs.Events.ContractMegucaEvent import ContractMegucaEvent
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
        
new_state = State(manager)

# Select a meguca as the meguca to apply the ContractMeguca Event to (would normally be set by other event)

new_state.GetEventData("NewContractableMegucaEvent")["new_meguca_id"] = random.choice(list(new_city.potential_megucas.keys()))

# Write to db.
new_state.WriteState()

manager.Commit()

recovered_state = State(manager)

event_instance = ContractMegucaEvent(new_city)

print(event_instance.Run(recovered_state))