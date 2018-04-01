from typing import Any, Dict, Tuple
from Objs.Meguca.Meguca import Meguca
from Objs.MegucaCity.MegucaCity import MegucaCity
from Objs.Communications.EventResponse import *
from Objs.Utils.GlobalDefines import *

class Event:

    def __init__(self, meguca_city: MegucaCity, is_multistage_event: bool, event_display_name: str = None,
                 base_weight: float = 1.0, stat_modifiers: Dict[str, float] = {}):
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

        # We always use the name of the class as the name of the event
        self.event_name = self.__class__.__name__

        self.city = meguca_city
        self.state = state
        self.is_multistage_event = is_multistage_event

        if event_display_name is None:
            event_display_name = self.event_name
        self.event_display_name = event_display_name
        
        self.base_weight = base_weight
        self.stat_modifiers = stat_modifiers
        
        for key in stat_modifiers:
            assert(key in MEGUCA_STATS)

        # Used for higher level probability calculations.
        self.weight_denominator = sum(stat_modifiers.values())**(WEIGHT_POWER) if stat_modifiers else 1
        
    def WeightForMeguca(self, meguca: Meguca):
        # TODO: Document this, what does it do?
        meguca_weight = 0
        for key, value in self.stat_modifiers.items():
            meguca_weight += meguca.stat_contributions[key] * value

        if 0 == len(self.stat_modifiers):
            # For events that are meguca-independent.
            meguca_weight = 1

        return meguca_weight**WEIGHT_POWER
        
    # These are meant as effectively "Virtual" classes, more documentation of methods Events are
    # expected to implement than anything.
    def Run(self, state):
        raise NotImplementedError
        
    

























