import random

from Objs.Events.Event import *

# TODO: Make Random events their own base class to derive this from? Maybe...
class EmotionalWitchOutEvent(Event):
    base_weight = 1
    stat_modifiers = {"friendships": -1, "neuroticism": 1}
    is_multistage_event = False
    event_name = __name__
    event_display_name = event_name
    meguca_weights = {}

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city)
    
    @classmethod  # It is important for memory savings that this be a class method
    def GetValidMegucas(cls, city, state):
        return city.GetMegucasByTraits("contracted")

    def Run(self, state, vote_result=None):
        # Select a meguca by weight.
        list_valid = self.GetValidMegucas(self.city, state) 
        meguca = self.SelectMegucaByWeight(list_valid)
        # Meguca has become a witch.
        energy_gain = self.city.WitchMeguca(meguca.id, state)
        event_text = f"{meguca.GetFullName()} has lost control of her emotional state and has matured into a full grown witch. This event has generated {energy_gain} energy for the collective."
        return EventResponse(self.event_name, self.event_display_name, event_text)