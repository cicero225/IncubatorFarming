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

# Okay now to do this in batch, first let's make a couple of gucas.
for _ in range(10):
    new_city.NewSensorMeguca()

targets = {}
sensors = {}    
while True:
    oldtargets = copy(targets)
    oldsensors = copy(sensors)
    input()  # just a pause.
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