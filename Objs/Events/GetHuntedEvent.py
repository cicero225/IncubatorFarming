import random

from Objs.Events.Event import *
from Objs.Utils.GlobalDefines import ENERGY_CHANGES

# TODO: Make Random events their own base class to derive this from? Maybe... 
# OKAY definitely do the above when you get a chance. Add a function for checking that function is valid and
# opening template.
class GetHuntedEvent(Event):
    base_weight = 1.0
    stat_modifiers = {"aggression": 1, "bravery": 1}
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
        # Check that Truth is >0.33 as needed
        if not state.truth_level > 0.33:
            # For random events, returning None as the text implies the event was not valid.
            return EventResponse(self.event_name, self.event_display_name, None)
        list_valid = self.GetValidMegucas(self.city, state) 
        meguca = self.SelectMegucaByWeight(list_valid)
        energy_change = ENERGY_CHANGES["BODY_KILLED"]
        event_text = f"Due to illogical emotion, {meguca.GetFullName()} attacked and killed your current body. Lose {-energy_change} energy."
        not_bankrupt = state.ChangeEnergy(energy_change)
        if not_bankrupt:
            # TODO: HANDLE THIS BY implmenting how to pass this off to a bankruptcy event.
            pass
        # Pick a random sensor > 0 and lower it by 1.
        valid_sensors = [sensor for sensor, level in state.sensors.items() if level > 0]
        if valid_sensors:  # otherwise there's no sensors to damage...   
            chosen = random.choice(valid_sensors)
            state.ChangeSensors(chosen, -1)
            event_text += f" Sensor: {chosen} level lowered by 1 due to damage."
        return EventResponse(self.event_name, self.event_display_name, event_text)