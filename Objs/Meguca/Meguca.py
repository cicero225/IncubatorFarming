from typing import Any, List, Dict, Callable
import json
import random

from Objs.Utils.GlobalDefines import *
from Objs.Utils.UniqueIDAllocator import UniqueIDAllocator
from Objs.Meguca.Defines import *


class Meguca:
    
    ALLOCATOR = UniqueIDAllocator()  # Created at import time
    MEGUCA_STATS = MEGUCA_STATS
    # Not stats, but still part of the class.
    MEGUCA_FIXED_ATTRIBUTES = ["is_witch", "id", "personal_name", "surname", "wish_type", "friends", "family", "is_contracted", "is_dead"]
    MEGUCA_FIELD_NAMES = ["IsWitch", "MagicalGirlID", "PersonalName", "Surname", "WishType", "Friends", "Family", "IsContracted", "IsDead"]
    WISH_TYPES = WISH_TYPES
    
    # We effectively need two constructors: One that makes a new meguca entirely, and one that remakes one that was stored.
    # This initializes the attributes, but the actual "constructors" are MakeNew and RestoreFromSaved
    def __init__(self, cleanup: Callable=None, friend_tracker_list: List[Any]=None, family_tracker_list: List[Any]=None):
        self.id = None
        self.is_witch = False
        self.is_contracted = False
        self.is_dead = False
        self.personal_name = ""
        self.surname = ""
        self.wish_type = ""
        self.stats = {}
        self.friends = [] if friend_tracker_list is None else friend_tracker_list
        self.family = [] if family_tracker_list is None else family_tracker_list
        self.cleanup = cleanup
        self.stat_contributions = {}
        self.negative_stat_contributions = {}
    
    def __del__(self):
        if self.cleanup is not None:
            self.cleanup(self)
        if self.id is not None:
            self.ALLOCATOR.ReturnID(self.id)
    
    def __repr__(self):
        return_str_list = ["<Meguca class. Name: ", self.personal_name , " " , self.surname, " id: " ,  str(self.id) , "\nIs Witch: ",
                           str(self.is_witch), "\nIs Contracted: ", str(self.is_contracted), "\nIs Dead: ",
                           str(self.is_dead), "\nWish Type: ", self.wish_type, "\n"]
        for stat in self.MEGUCA_STATS:
            return_str_list.extend([stat, ": ", str(self.stats.get(stat, None)), "\n"])
        return_str_list.append(">")
        return "".join(return_str_list)
        
    def PrintFriends(self):
        # We don't want this in __repr__, because it might get very long and obnoxious. This makes it a manual call.
        output_string_list = ["Friends:"]
        for friend in self.friends:
            output_string_list.append(friend.GetFullName())
        return "\n".join(output_string_list)
        
    def PrintFamily(self):
        # We don't want this in __repr__, because it might get very long and obnoxious. This makes it a manual call.
        output_string_list = ["Family:"]
        for member in self.family:
            output_string_list.append(member.GetFullName())
        return "\n".join(output_string_list)
    
    def __eq__(self, other):
        return self.id == other.id
        
    def GetFullName(self):
        return self.personal_name + " " + self.surname
        
    def IncreaseStat(self, stat: str, change: int):
        full_range = self.MEGUCA_STATS[stat].full_range
        # I prefer this to the nested min/max, but tastes vary
        if change > 0:
            self.stats[stat] = min(full_range[1], self.stats[stat] + change)
        else:
            self.stats[stat] = max(full_range[0], self.stats[stat] + change)
            
    # Purely Convenience
    def DecreaseStat(self, stat: str, change: int):
        self.IncreaseStat(stat, -change)
    
    def PrecalculateStatModifiers(self):
        for key, value in self.stats.items():
            self.stat_contributions[key] = 2*value/(self.MEGUCA_STATS[key].full_range[0] + self.MEGUCA_STATS[key].full_range[1])
            
    def PrecalculateNegativeStatModifiers(self):
        for key, value in self.stats.items():
            self.negative_stat_contributions[key] = 2*(self.MEGUCA_STATS[key].full_range[1] - value)/(self.MEGUCA_STATS[key].full_range[0] + self.MEGUCA_STATS[key].full_range[1])
        
    @classmethod
    def MakeNew(cls, targets: Dict[str, int]=None, sensors: Dict[str, int]=None, friends=None, family=None, cleanup: Callable=None):   
        if targets is None:
            targets = {}
        if sensors is None:
            sensors = {}
        if friends is None:
            friends = []
        if family is None:
            family = []    
        new_meguca = cls(cleanup, friend_tracker_list=friends, family_tracker_list=family)
        new_meguca.id = new_meguca.ALLOCATOR.GetNewID()
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
        new_meguca.PrecalculateStatModifiers()
        new_meguca.PrecalculateNegativeStatModifiers()
        return new_meguca

    def RandomizeName(self) -> None:
        self.personal_name =  random.choice(list(FIRST_NAME_POOL | EITHER_NAME_POOL))
        self.surname = random.choice(list(LAST_NAME_POOL | EITHER_NAME_POOL - {self.personal_name}))

    def RandomizeWish(self) -> None:
        self.wish_type = random.choice(self.WISH_TYPES)
    
    # Outputs a version of this object that is suitable for writing to the sqlite db
    def ToMegucaRow(self, city_id):
        # A little bit of hardcoding... damn, this is awkward. Namedtuple is not as practical as I'd wish.
        result_args = []
        for i, name_tuple in enumerate(MEGUCA_TABLE_FIELDS):
            name = name_tuple[0]
            if name in ["Friends", "Family"]:
                result_args.append(json.dumps([x.id for x in getattr(
                                   self, self.MEGUCA_FIXED_ATTRIBUTES[self.MEGUCA_FIELD_NAMES.index(name)])]))
            elif name == "Stats":
                result_args.append(json.dumps(self.stats))
            elif name == "CityID":
                result_args.append(city_id)
            else:
                result_args.append(getattr(self, self.MEGUCA_FIXED_ATTRIBUTES[self.MEGUCA_FIELD_NAMES.index(name)]))
        return MEGUCA_ROW(*result_args)
    
    # Unfortunately, this can't fully reconstruct the object (as it needs references to other megucas). A second call to
    # ReconstructFriendsAndFamily is necessary once all megucas are available.
    @classmethod
    def FromMegucaRow(cls, meguca_row, cleanup: Callable=None):
        new_meguca = cls(cleanup=cleanup)
        for i, name in enumerate(cls.MEGUCA_FIELD_NAMES):
            if name == "Friends":
                new_meguca.friends[:] = json.loads(meguca_row.Friends)
            elif name == "Family":
                new_meguca.family[:] = json.loads(meguca_row.Family)
            else:
                setattr(new_meguca, cls.MEGUCA_FIXED_ATTRIBUTES[i], getattr(meguca_row, name))
        new_meguca.stats = json.loads(meguca_row.Stats)
        new_meguca.PrecalculateStatModifiers()
        new_meguca.PrecalculateNegativeStatModifiers()
        return new_meguca
        
    def ReconstructFriendsAndFamily(self, lookup_table: Dict[int, Any]):
        # lookup_table is a dict from the id -> Meguca, and can be generated by for instance a complete
        # RelationshipTracker id_member_lookup.
        for i, id in enumerate(self.friends):
            self.friends[i] = lookup_table[id]
        for i, id in enumerate(self.family):
            self.family[i] = lookup_table[id]

    def MakeMegucaDisplay(self, state):
        # TODO: Add Wish Type display
        stat_display_list = []
        for stat, behavior in MEGUCA_STATS.items():
            if behavior.default_visible or state.sensors[stat] > 0: 
                stat_display_list.append(f"{stat}: {self.stats[stat]}")
        stat_display_list.sort()
        stat_display_string = '\n'.join(stat_display_list)
        return f"{self.GetFullName()}\n\nStats:\n{stat_display_string}"
            
    # Todo: need function for determining if a girl accepts contract or not.
    