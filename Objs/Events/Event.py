from typing import Any, Dict, Tuple
from Objs.Meguca.Meguca import Meguca
from Objs.MegucaCity.MegucaCity import MegucaCity
from Objs.Communications.EventResponse import *
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
        # TODO: Document this, what does it do?
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
        return new_weight
        
    # These are meant as effectively "Virtual" classes, more documentation of methods Events are
    # expected to implement than anything.
    def Run(self, state: State, vote_result=None):
        raise NotImplementedError
        
    

























