# Test Script to test some stuff
from copy import copy
import random

from Objs.Utils.GlobalDefines import *

from Objs.MegucaCity.MegucaCity import MegucaCity


new_city = MegucaCity()



# A simple test cycle. Set sensors, get new meguca, get new friend meguca, decay potential.
print("New Meguca!")
new_meguca = new_city.NewSensorMeguca()
print(new_meguca)

new_city.ContractMeguca(new_meguca.id)

friend_meguca = random.choice(list(new_city.contracted_megucas.values()))
print(friend_meguca.GetFriendlyName() + " brings friend!")
new_friend = new_city.NewMegucaFromFriend(friend_meguca)
print(new_friend)

print("But we don't contract.")

print("Decaying Potential...")
lost = new_city.PotentialDecay()
if lost:
    print("These megucas have lost potential and may no longer be contracted:")
    for l in lost:
        print(l.GetFriendlyName())
del lost

# Okay now to do this in batch, first let's make a bunch of gucas.
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

# Test the search feature
print("Demoing Search. Enter q to quit")
meguca_types = ["contracted", "potential", "witch", "dead", None]
wish_types_or_none = list(WISH_TYPES)
wish_types_or_none.append(None)
while True:
    valid_range = {}
    for stat, sensor_item in MEGUCA_STATS.items():
        if random.random() < 0.33:
            range = [random.randint(sensor_item.full_range[0], sensor_item.full_range[1]),
                     random.randint(sensor_item.full_range[0], sensor_item.full_range[1])]
            if range[1] > range[0]:
                valid_range[stat] = (range[0] if random.random() < 0.8 else None, range[1] if random.random() < 0.8 else None)
            else:
                valid_range[stat] = (range[1] if random.random() < 0.8 else None, range[0] if random.random() < 0.8 else None)
    meguca_type = random.choice(meguca_types)
    wish_type = random.choice(wish_types_or_none)
    print(meguca_type)
    print(wish_type)
    print(valid_range)
    found_megucas = new_city.GetMegucasByTraits(meguca_type, wish_type, valid_range)
    for meguca in found_megucas:
        print(meguca)
        print(meguca.PrintFriends())
        print(meguca.PrintFamily())
    leave = input()
    if (leave == "q"):
        break

print("Demoing Sensors. Enter q to quit")
        
targets = {}
sensors = {}    
while True:
    oldtargets = copy(targets)
    oldsensors = copy(sensors)
    str_sensor = random.choice(list(MEGUCA_STATS))
    sensor_level = random.randint(0, 2)
    print("Setting " + str_sensor + " sensor to " + str(sensor_level))
    sensors[str_sensor] = sensor_level
    target = 0
    while not target:
        target = random.randint(-1, 5)
    if target != -1:
        targets[str_sensor] = target
    print("Setting target to " + str(target))
    print("New Meguca!")
    new_meguca = new_city.NewSensorMeguca(targets, sensors)
    print(new_meguca)
    if random.random() > 0.5:
        print("Contracting Meguca...")
        new_city.ContractMeguca(new_meguca.id)
    else:
        print("We did not contract!")
    
    if new_city.contracted_megucas:
        friend_meguca = random.choice(list(new_city.contracted_megucas.values()))
        print(friend_meguca.GetFriendlyName() + " brings friend!")
        new_friend = new_city.NewMegucaFromFriend(friend_meguca)
        print(new_friend)
        if random.random() > 0.5:
            print("Contracting Meguca...")
            new_city.ContractMeguca(new_friend.id)
        else:
            print("We did not contract!")
    
    print("Decaying Potential...")
    lost = new_city.PotentialDecay()
    if lost:
        print("These megucas have lost potential and may no longer be contracted.")
        for l in lost:
            print(l.GetFriendlyName())
    leave = input()
    if (leave == "q"):
        break