from typing import Any, Dict, Tuple
from Objs.Meguca.Meguca import Meguca
from Objs.MegucaCity.MegucaCity import MegucaCity
from Objs.Communications.EventResponse import *
from Objs.Utils.BaseUtils import WeightedDictRandom
from Objs.Utils.GlobalDefines import *
from Objs.State.State import State

class Event:
    # It's important (to avoid needing to instantiate events to save memory) that this be set at import time. Note that derived classes do not inherit this.
    base_weight = 1.0
    stat_modifiers = {}
    is_multistage_event = None
    # These two should be reflected in every derived class.
    event_name = __name__
    event_display_name = event_name
    last_stage = 0  # The last integer stage of this even (0 is event is single-stage)
    meguca_weights = None  # caches the results of WeightForMeguca if it needs to get called more than once. This is here more as a reminder - the derived class must set this to {}!
    
    # TODO: Document missing arguments.
    def __init__(self, meguca_city: MegucaCity):
        """
        Initializes an Event.
        This class is not meant to be used, only inherited from.
        :param meguca_city: The MegucaCity instance used by the game. The event requires it to
                            execute changes to the state of the game.
        :param state: A state object or dict that contains any information about the state of the game not
                      included in meguca_city.
        :param is_multistage_event: A boolean value of if the event is multistage or not.
        :param event_display_name: The display name of the event. If None then the name of the event class will
                                   be used
        """

        self.city = meguca_city       
        # check this at runtime
        for key in self.stat_modifiers:
            assert(key in MEGUCA_STATS)
    
    @classmethod
    def GetWeightDenominator(cls):
        # Used for higher level probability calculations.
        return sum(abs(x) for x in cls.stat_modifiers.values())**(WEIGHT_POWER) if cls.stat_modifiers else 1
    
    # Note: On derived classes, this will properly use the derived class rather than base class.
    @classmethod
    def WeightForMeguca(cls, meguca: Meguca):
        # Get the relative weight contributed by each individual meguca to the overall probability calculation.
        # Also used to influence meguca selection when choosing megucas for events.
        new_weight = cls.meguca_weights.get(meguca.id)
        if new_weight is not None:
            return new_weight
        meguca_weight = 0
        for key, value in cls.stat_modifiers.items():
            if value > 0:
                meguca_weight += meguca.stat_contributions[key] * value
            elif value < 0:
                meguca_weight += meguca.negative_stat_contributions[key] * -value

        if 0 == len(cls.stat_modifiers):
            # For events that are meguca-independent.
            meguca_weight = 1

        new_weight = meguca_weight**WEIGHT_POWER
        cls.meguca_weights[meguca.id] = new_weight
        return new_weight
    
    @classmethod
    def SelectMegucaByWeight(cls, megucas: List[Meguca]):
        # Pick a meguca based on the results of WeightForMeguca
        weight_dict = {meguca.id: cls.WeightForMeguca(meguca) for meguca in megucas}
        random_id = WeightedDictRandom(weight_dict)[0]
        # Kind of awkward but oh well.
        for meguca in megucas:
            if random_id == meguca.id:
                return meguca
    
    # These are meant as effectively "Virtual" classes, more documentation of methods Events are
    # expected to implement than anything.
    def Run(self, state: State, vote_result=None):
        raise NotImplementedError
        
    

























