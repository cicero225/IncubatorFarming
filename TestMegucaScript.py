# Test Script to test some stuff
from copy import copy

from Objs.Utils.GlobalDefines import *

from Objs.Meguca.Meguca import Meguca


new_meguca = Meguca.MakeNew()

print("Full Random Meguca:")
print(new_meguca)

print("Available Stats: (Note: this ignores sensor visibility for now)")
for stat in MEGUCA_STATS:
    print(stat)

targets = {}
sensors = {}    
while True:
    oldtargets = copy(targets)
    oldsensors = copy(sensors)
    try:
        str_sensor = input("Set Sensor? (Type name)")
        assert(str_sensor in MEGUCA_STATS)
        sensor_level = int(input("Set Sensor Level (0-indexed)?"))
        sensors[str_sensor] = sensor_level
        target = int(input("Set Target? (-1 if nothing)"))
        if target != -1:
            targets[str_sensor] = target
        new_meguca = Meguca.MakeNew(targets, sensors)        
        print(new_meguca)
    except:
        print("Not valid!")
        targets = oldtargets
        sensors = oldsensors