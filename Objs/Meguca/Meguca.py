from typing import Any, Dict
import random

from Objs.Utils.GlobalDefines import *
from Objs.Utils.UniqueIDAllocator import UniqueIDAllocator
from Objs.Meguca.Defines import *


class Meguca:
    
    ALLOCATOR = UniqueIDAllocator()  # Created at import time
    MEGUCA_STATS = MEGUCA_STATS
    # Not stats, but still part of the class.
    MEGUCA_FIXED_ATTRIBUTES = ["is_witch", "id", "personal_name", "surname", "wish_type", "friends", "family", "is_contracted"]
    WISH_TYPES = WISH_TYPES
    
    # We effectively need two constructors: One that makes a new meguca entirely, and one that remakes one that was stored.
    # This initializes the attributes, but the actual "constructors" are MakeNew and RestoreFromSaved
    def __init__(self):
        self.id = self.ALLOCATOR.GetNewID()
        self.is_witch = False
        self.is_contracted = False
        self.personal_name = ""
        self.surname = ""
        self.wish_type = ""
        self.stats = {}
        self.friends = []
        self.family = []
    
    def __del__(self):
        if self.id is not None:
            self.ALLOCATOR.ReturnID(self.id)
    
    def __repr__(self):
        return_str_list = ["<Meguca class. Name: ", self.personal_name + " " + self.surname, "\nIs Witch: ",
                           str(self.is_witch), "\nWish Type: ", self.wish_type, "\n"]
        for stat in self.MEGUCA_STATS:
            return_str_list.extend([stat, ": ", str(self.stats.get(stat, None)), "\n"])
        return_str_list.append(">")
        return "".join(return_str_list)
        
    def GetFriendlyName(self):
        return self.personal_name + " " + self.surname

    @classmethod
    def MakeNew(cls, targets: Dict[str, int]=None, sensors: Dict[str, int]=None, friends=None, family=None):
        if targets is None:
            targets = {}
        if sensors is None:
            sensors = {}
        if friends is None:
            friends = []
        if family is None:
            family = []    
        new_meguca = cls()
        new_meguca.friends = friends
        new_meguca.family = family
        new_meguca.RandomizeName()
        new_meguca.RandomizeWish()
        for stat, sensor_behavior in cls.MEGUCA_STATS.items():
            sensor_range = sensor_behavior.sensor_range[sensors.get(stat, 0)]
            target = targets.get(stat, None)
            if not sensor_behavior.targetable and sensor_range != -1:
                new_meguca.stats[stat] = random.randint(max(sensor_behavior.full_range[0], sensor_behavior.optimum - sensor_range),
                                                  min(sensor_behavior.full_range[1], sensor_behavior.optimum + sensor_range))
            elif target is None or sensor_range == -1:
                new_meguca.stats[stat] = random.randint(sensor_behavior.full_range[0], sensor_behavior.full_range[1])
            else:
                new_meguca.stats[stat] = random.randint(max(sensor_behavior.full_range[0], target - sensor_range),
                                                        min(sensor_behavior.full_range[1], target + sensor_range))
        return new_meguca

    def RandomizeName(self) -> None:
        self.personal_name =  random.choice(list(FIRST_NAME_POOL | EITHER_NAME_POOL))
        self.surname = random.choice(list(LAST_NAME_POOL | EITHER_NAME_POOL - {self.personal_name}))

    def RandomizeWish(self) -> None:
        self.wish_type = random.choice(self.WISH_TYPES)
        
    def RestoreFromSaved(self):
        pass
        
    # Todo: need function for determining if a girl accepts contract or not.
    