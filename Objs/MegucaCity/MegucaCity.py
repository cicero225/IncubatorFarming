from Objs.Utils.GlobalDefines import *
from Objs.Utils.BaseUtils import WeightedDictRandom

from Objs.Meguca.Meguca import Meguca
from Objs.Meguca.Defines import *
from Objs.MegucaCity.Defines import *
from Objs.RelationshipTracker.RelationshipTracker import RelationshipTracker
from Objs.Utils.UniqueIDAllocator import UniqueIDAllocator

import itertools
import random
import warnings
from typing import Any, Dict, Tuple


# Should have ownership of all Meguca objects. Handles allocating and deallocating megucas, and is used to track
# megucas, witches, and potential contractees.
class MegucaCity:

    MEGUCA_POPULATION = MEGUCA_POPULATION

    def __init__(self, city_id):  # Makes an empty city
        self.contracted_megucas = {}   # dict[int id, Meguca]
        self.potential_megucas = {}
        self.witches = {}
        self.dead_megucas = {}  # That is not dead which can eternal lie.
        self.all_names = set()  # Just making sure we don't get duplicate megucas with the same name.
        self.friends_tracker = RelationshipTracker()
        self.family_tracker = RelationshipTracker()
        self.city_id = city_id
        self.original_read_dict = {}  # the original db read in when this object was created, if any.
    
    def GetMegucaById(self, id: int) -> Meguca:
        for look_in in [self.contracted_megucas, self.potential_megucas, self.witches, self.dead_megucas]:
            maybe = look_in.get(id)
            if maybe is not None:
                return maybe
    
    # Search function to expedite finding megucas for events.
    # meguca_type: contracted, potential, witch, or dead
    # wish_type: A member of GlobalDefines.WISH_TYPES
    # valid_range: dict from string stat -> Lowest valid value, highest valid value. (None if no limit specified).
    # Not all keys need to be provided. (Note that the values are *inclusive*)
    def GetMegucasByTraits(self, meguca_type: str=None, wish_type: str=None, valid_range: Dict[str, Tuple[int]]=None):
        # This is a straight O(N) one-by-one check. If you want faster, drawing on the original relational database might work. However, this should suffice for the most common purposes.
        assert wish_type is None or wish_type in WISH_TYPES
        string_dict = {"contracted": self.contracted_megucas,
                       "potential": self.potential_megucas,
                       "witch": self.witches,
                       "dead": self.dead_megucas}
        all_valid = []
        for look_in in (list(string_dict.values()) if meguca_type is None else (string_dict[meguca_type],)):
            for id, meguca in look_in.items():
                if wish_type is not None and meguca.wish_type != wish_type:
                    continue
                if valid_range is not None:
                    proceed = True
                    for stat_name, stat_range in valid_range.items():
                        this_stat = meguca.stats[stat_name]
                        if stat_range[0] is not None and this_stat < stat_range[0]:
                            proceed = False
                            break
                        if stat_range[1] is not None and this_stat > stat_range[1]:
                            proceed = False
                            break
                    if not proceed:
                        continue
                all_valid.append(meguca)
        return all_valid
    
    # A bit repetitive, but...
    def ContractMeguca(self, id: int):
        self.contracted_megucas[id] = self.potential_megucas[id]
        del self.potential_megucas[id]
        self.contracted_megucas[id].is_contracted = True
        
    def WitchMeguca(self, id: int):
        self.witches[id] = self.contracted_megucas[id]
        del self.contracted_megucas[id]
        self.witches[id].is_witch = True
        
    def KillPotential(self, id: int):
        self.dead_megucas[id] = self.potential_megucas[id]
        del self.potential_megucas[id]
        self.dead_megucas[id].is_dead = True
        
    def KillMeguca(self, id: int):
        self.dead_megucas[id] = self.contracted_megucas[id]
        del self.contracted_megucas[id]
        self.dead_megucas[id].is_dead = True
        
    def KillWitch(self, id: int):
        self.dead_megucas[id] = self.witches[id]
        del self.witches[id]
        self.dead_megucas[id].is_dead = True
    
    def MegucaCleanupFunctor(self, meguca: Meguca):
        self.friends_tracker.RemoveMember(meguca)
        self.family_tracker.RemoveMember(meguca)
    
    def NewSensorMeguca(self, targets: Dict[str, int]=None, sensors: Dict[str, int]=None, friends: List[Any]=None) -> Meguca:
        if friends is None:
            friends = []
        else:
            # rare edge case check to avoid infinite loops
            all_surnames = set(x.surname for x in friends)
            if len(all_surnames) >= len(LAST_NAME_POOL) + len(EITHER_NAME_POOL):
                warnings.warn("Exhausted surname pool! Dropping a friend.")
                friends.remove(random.choice(friends))
        # Make a new meguca, and also figure out who their friends/family are, if any. friends, if provided, will be used as a list of guaranteed friends.
        # Returns whoever this meguca is.
        new_meguca = Meguca.MakeNew(targets, sensors, cleanup=self.MegucaCleanupFunctor)
        new_meguca.friends = self.friends_tracker.Get(new_meguca)
        new_meguca.family = self.family_tracker.Get(new_meguca)
        while True:
            # avoid same surname
            proceed = True
            while True:
                proceed = True
                for friend in friends:
                    if friend.surname == new_meguca.surname:
                        new_meguca.RandomizeName()
                        proceed = False
                        break
                if proceed:
                    break
            if not proceed:
                continue
            while True:
                proceed = True
                if new_meguca.GetFriendlyName() in self.all_names:
                    new_meguca.RandomizeName()
                    proceed = False
                else:
                    break
            if proceed:
                break
        self.all_names.add(new_meguca.GetFriendlyName())   
        # A simple approach. Each meguca has as many contractable friends as their friendships stat.
        # It is assumed that all of these must lie in the pool of potential_megucas + contracted_megucas + witches + dead_megucas = MEGUCA_POPULATION + dead_megucas (we include dead megucas to prevent numerical issues)
        # The probability of a given friend of theirs already being in the pool controlled by frienships stat and this population count.
        # However, we must first determine family, as that supersedes friends.
        already_used = set([x.id for x in friends])
        # TODO: It would be fun flavorwise for girls who have dead/witched friends to be able to bring them back in their wish,
        # or to have altered stats, but we can save that for later (especially since the stats would have to somehow work with
        # the sensors.)
        # We will need this merged dict no matter what anyway.
        all_potential_gucas = {**self.contracted_megucas, **self.potential_megucas,
                               **self.witches, **self.dead_megucas}
        friendship_weights = {id: meguca.stats["friendships"] for id, meguca in all_potential_gucas.items() if meguca not in friends}
        for id, meguca in all_potential_gucas.items():
            if meguca.surname == new_meguca.surname:
                self.family_tracker.Connect(meguca, new_meguca)
                del friendship_weights[id]
                already_used.add(id)
        # add guaranteed friends
        self.friends_tracker.AddMultiple(new_meguca, friends)
        for _ in range(new_meguca.stats["friendships"] - len(friends)):
            prob_already_exists_friend = (sum(weight for id, weight in friendship_weights.items())/
                                          (3*(MEGUCA_POPULATION + len(self.dead_megucas))))
            # if friend doesn't already exist, we ignore it unless they get pulled later by the NewMegucaFromFriend event.
            if random.random() < prob_already_exists_friend:
                while True:
                    id = WeightedDictRandom(friendship_weights)[0]
                    if id in already_used:
                        continue
                    meguca = all_potential_gucas[id]
                    self.friends_tracker.Connect(new_meguca, meguca)
                    # NOTE: This procedure will often give megucas more friends than their friendships stat strictly dictates.
                    # This is FINE, and a deliberate feature, not a bug. It could be corrected here with an if statement if we really
                    # wanted.
                    del friendship_weights[id]
                    already_used.add(id)
                    break
        
        self.potential_megucas[new_meguca.id] = new_meguca
        return new_meguca
        
        
    def NewMegucaFromFriend(self, friend: Meguca) -> Meguca:
        # No sensors are involved in this; a friend is pulled based on the friends/family of an existing meguca, or a completely
        # new random friend is created.
        # First we check if the meguca even has any friends who are potential contractees.
        potential_contractee_friends = [f for f in itertools.chain(friend.friends, friend.family) if f.id in self.potential_megucas]
        number_potential_new_meguca = max(friend.stats["friendships"] - len(friend.friends), 0)
        if not number_potential_new_meguca and not potential_contractee_friends:
            warnings.warn("Attempted to summon friend in invalid situation (Not a bug in certain kinds of tests)")
            prob_new_meguca = 1
        else:
            prob_new_meguca = number_potential_new_meguca/(number_potential_new_meguca + len(potential_contractee_friends))
        if random.random() > prob_new_meguca:
            # use existing friend or family member.
            return self.potential_megucas[random.choice(potential_contractee_friends).id]
        # Make new meguca and guarantee that they are already friends here
        return self.NewSensorMeguca(friends=[friend])
        
    def PotentialDecay(self) -> List[Meguca]:  # When called, causes megucas waiting in the potential pool to randomly lose potential (deallocate)
        potential_lost = []
        for id, meguca in self.potential_megucas.items():
            chance_lost_potential = 1 - meguca.stats["potential"]/6
            if random.random() < chance_lost_potential: # Potential lost.
                if meguca.cleanup(meguca) is not None:
                    meguca.cleanup(meguca)
                potential_lost.append(meguca)
        for meguca in potential_lost:
            del self.potential_megucas[meguca.id]  # Note that potential_lost is now the only owner of these objects.
            self.all_names.remove(meguca.GetFriendlyName())
        return potential_lost
                
    def WriteCityToDB(self, manager, forced=False):
        # Comparing the new dict with the old dict is computationally expensive, but probably
        # worth it to avoid the code maintenance nightmare of explicitly tracking which megucas
        # are changed.
        write_dict = {}
        for meguca in itertools.chain(
            self.contracted_megucas.values(),
            self.potential_megucas.values(),
            self.witches.values(),
            self.dead_megucas.values()):
            meguca_row = meguca.ToMegucaRow(self.city_id)
            this_key = frozenset(getattr(meguca_row, x) for x in MEGUCA_PRIMARY_KEYS)
            # rather then invoke many SQL operations to do this, probably better to handle it here
            orig_meguca = self.original_read_dict.get(this_key, (None, None))[0]
            # One row dict.
            # Note: None != meguca_row evalutates to true, which is what we'd want.
            write_dict[this_key] = (meguca_row, orig_meguca != meguca_row)

        manager.WriteTable(write_dict, [x[0] for x in MEGUCA_TABLE_FIELDS], table=MEGUCA_TABLE_NAME, forced=forced)
        
        # Drop Megucas that were deleted.
        for deleted_meguca in set(self.original_read_dict) - set(write_dict):
            manager.DeleteRows({x: getattr(deleted_meguca, x) for x in MEGUCA_PRIMARY_KEYS},
                               table=MEGUCA_TABLE_NAME, forced=forced)
    
    @classmethod
    def ReadCityFromDb(cls, city_id, manager):
        new_city = cls(city_id)
        new_city.original_read_dict = manager.ReadTable(MEGUCA_ROW, MEGUCA_PRIMARY_KEYS, {"CityID": new_city.city_id} , table=MEGUCA_TABLE_NAME, read_flag="may_be_modified")
        used_ids = list()
        for primary_keys, row_tuple in new_city.original_read_dict.items():
            row = row_tuple[0]
            new_meguca = Meguca.FromMegucaRow(row, new_city.MegucaCleanupFunctor)
            new_city.friends_tracker.Set(new_meguca, new_meguca.friends)
            new_city.family_tracker.Set(new_meguca, new_meguca.family)
            used_ids.append(new_meguca.id)
            new_city.all_names.add(new_meguca.GetFriendlyName())
            if new_meguca.is_dead:
                new_city.dead_megucas[new_meguca.id] = new_meguca
            elif new_meguca.is_witch:
                new_city.witches[new_meguca.id] = new_meguca
            elif new_meguca.is_contracted:
                new_city.contracted_megucas[new_meguca.id] = new_meguca
            else:
                new_city.potential_megucas[new_meguca.id] = new_meguca
        used_ids.sort()
        # Override allocator with new ID set.
        Meguca.ALLOCATOR = UniqueIDAllocator.RestoreFromSaved(used_ids[1], list(set(range(0, used_ids[1] + 1)) - set(used_ids)))
        all_potential_gucas = {**new_city.contracted_megucas, **new_city.potential_megucas,
                               **new_city.witches, **new_city.dead_megucas}
        # We can only do this once all megucas are in place.
        for meguca in all_potential_gucas.values():
            meguca.ReconstructFriendsAndFamily(all_potential_gucas)
        return new_city
                
    # Todo need functions for girl contracting, witching