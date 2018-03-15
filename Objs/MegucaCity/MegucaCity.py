from Objs.Utils.GlobalDefines import *
from Objs.Utils.BaseUtils import WeightedDictRandom

from Objs.Meguca.Meguca import Meguca
from Objs.MegucaCity.Defines import *

import itertools
import random
import warnings
from typing import Any, Dict


# Should have ownership of all Meguca objects. Handles allocating and deallocating megucas, and is used to track
# megucas, witches, and potential contractees.
class MegucaCity:

    MEGUCA_POPULATION = MEGUCA_POPULATION

    def __init__(self):  # Makes an empty city
        self.contracted_megucas = {}   # dict[int id, Meguca]
        self.potential_megucas = {}
        self.witches = {}
        self.dead_megucas = {}  # That is not dead which can eternal lie.
        self.all_names = set()  # Just making sure we don't get duplicate megucas with the same name.
    
    def GetMegucaById(self, id: int) -> Meguca:
        for look_in in [self.contracted_megucas, self.potential_megucas, self.witches, self.dead_megucas]:
            maybe = look_in.get(id)
            if maybe is not None:
                return maybe
    
    def ContractMeguca(self, id: int):
        self.contracted_megucas[id] = self.potential_megucas[id]
        del self.potential_megucas[id]
        self.contracted_megucas[id].is_contracted = True
    
    def MegucaCleanupFunctor(self, meguca: Meguca):
        for id in meguca.friends:
            potential = self.GetMegucaById(id)
            if potential is not None:  # Megucas are sometimes destroyed together, so sometimes the friend being looked for is already gone.
                potential.friends.remove(meguca.id)
        for id in meguca.family:
            potential = self.GetMegucaById(id)
            if potential is not None:
                potential.family.remove(meguca.id)
    
    def NewSensorMeguca(self, targets: Dict[str, int]=None, sensors: Dict[str, int]=None, friends: List[int]=None) -> Meguca:
        if friends is None:
            friends = []
        # Make a new meguca, and also figure out who their friends/family are, if any. friends, if provided, will be used as a list of guaranteed friends.
        # Returns whoever this meguca is.
        while True:
            new_meguca = Meguca.MakeNew(targets, sensors, cleanup=self.MegucaCleanupFunctor)
            if new_meguca.GetFriendlyName() not in self.all_names:
                self.all_names.add(new_meguca.GetFriendlyName())
                break
        # A simple approach. Each meguca has as many contractable friends as their friendships stat.
        # It is assumed that all of these must lie in the pool of potential_megucas + contracted_megucas + witches + dead_megucas = MEGUCA_POPULATION + dead_megucas (we include dead megucas to prevent numerical issues)
        # The probability of a given friend of theirs already being in the pool controlled by frienships stat and this population count.
        # However, we must first determine family, as that supersedes friends.
        already_used = set(friends)
        # TODO: It would be fun flavorwise for girls who have dead/witched friends to be able to bring them back in their wish,
        # or to have altered stats, but we can save that for later (especially since the stats would have to somehow work with
        # the sensors.)
        # We will need this merged dict no matter what anyway.
        all_potential_gucas = {**self.contracted_megucas, **self.potential_megucas,
                               **self.witches, **self.dead_megucas}
        friendship_weights = {id: meguca.stats["friendships"] for id, meguca in all_potential_gucas.items() if id not in friends}
        for id, meguca in all_potential_gucas.items():
            if meguca.surname == new_meguca.surname:
                new_meguca.family.append(id)
                meguca.family.append(new_meguca.id)
                del friendship_weights[id]
                already_used.add(id)
        # add guaranteed friends
        new_meguca.friends.extend(friends)
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
                    new_meguca.friends.append(id)
                    # NOTE: This procedure will often give megucas more friends than their friendships stat strictly dictates.
                    # This is FINE, and a deliberate feature, not a bug. It could be corrected here with an if statement if we really
                    # wanted.
                    meguca.friends.append(new_meguca.id)
                    del friendship_weights[id]
                    already_used.add(id)
                    break
        
        self.potential_megucas[new_meguca.id] = new_meguca
        return new_meguca
        
        
    def NewMegucaFromFriend(self, friend: Meguca) -> Meguca:
        # No sensors are involved in this; a friend is pulled based on the friends/family of an existing meguca, or a completely
        # new random friend is created.
        # First we check if the meguca even has any friends who are potential contractees.
        potential_contractee_friends = [f for f in itertools.chain(friend.friends, friend.family) if f in self.potential_megucas]
        number_potential_new_meguca = max(friend.stats["friendships"] - len(friend.friends), 0)
        if not number_potential_new_meguca and not potential_contractee_friends:
            warnings.warn("Attempted to summon friend in invalid situation (Not a bug in certain kinds of tests)")
            prob_new_meguca = 1
        else:
            prob_new_meguca = number_potential_new_meguca/(number_potential_new_meguca + len(potential_contractee_friends))
        if random.random() > prob_new_meguca:
            # use existing friend or family member.
            return self.potential_megucas[random.choice(potential_contractee_friends)]
        # Make new meguca and guarantee that they are already friends here
        return self.NewSensorMeguca(friends=[friend])
        
    def PotentialDecay(self) -> List[Meguca]:  # When called, causes megucas waiting in the potential pool to randomly lose potential (deallocate)
        potential_lost = []
        for id, meguca in self.potential_megucas.items():
            chance_lost_potential = 1 - meguca.stats["potential"]/6
            if random.random() < chance_lost_potential: # Potential lost.
                potential_lost.append(self.potential_megucas[id])
        for meguca in potential_lost:
            del self.potential_megucas[meguca.id]  # Note that potential_lost is now the only owner of these objects.
            self.all_names.remove(meguca.GetFriendlyName())
        return potential_lost
                
    # Todo need functions for girl contracting, witching