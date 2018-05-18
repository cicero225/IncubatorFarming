import random

from Objs.Events.Phase import Phase
from Objs.MegucaCity.MegucaCity import MegucaCity
from Objs.Utils.BaseUtils import WeightedDictRandom

# Events.
from Objs.Events.NotAfraidOfAnythingAnymoreEvent import NotAfraidOfAnythingAnymoreEvent
from Objs.Events.SlowPeriodEvent import SlowPeriodEvent
from Objs.Events.GetHuntedEvent import GetHuntedEvent

# Represents a random event.

class RandomEventPhase(Phase):
    is_multistage_event = False
    event_name = __name__
    event_display_name = event_name
    
    def __init__(self, meguca_city: MegucaCity):
        super().__init__(meguca_city, valid_events =
                         {NotAfraidOfAnythingAnymoreEvent.event_name: NotAfraidOfAnythingAnymoreEvent,
                          SlowPeriodEvent.event_name: SlowPeriodEvent,
                          GetHuntedEvent.event_name: GetHuntedEvent})
                          
    def Run(self, state, vote_result):
        # Check if we're already running an event
        new_event = state.GetEventData(self.event_name).get("CurrentEvent")
        if new_event:
            # Continue the previous event.
            output = self.RunEvent(new_event, state, vote_result)
        else:
            # If not, pick a random event.
            # First parse the event probabilities
            weight_dict = {}
            for event in self.valid_events.values():
                weight_dict[event.event_name] = event.base_weight * sum(event.WeightForMeguca(meguca) for meguca in event.GetValidMegucas(self.city, state))/event.GetWeightDenominator()
            valid = None
            while valid is None:            
                # Pick a random event
                list_events = WeightedDictRandom(weight_dict)
                # Instantiate the event and run it.
                new_event = list_events[0]
                output = self.RunEvent(new_event, state, vote_result)
                valid = output.output_text
                # If none, the event failed to run. To preempt potential problems, let's remove it from the weight dict.
                if valid is None:
                    del weight_dict[new_event]
                    if not weight_dict:
                        raise AssertionError("NoValidEvents!")
        # Check whether event is done and freeze this phase waiting for the next phase if not.
        if not Phase.CheckIfEventDone(state, new_event):
            state.SetEventDone(self.event_name, False)
            state.GetEventData(self.event_name)["CurrentEvent"] = new_event
            return output        
        state.GetEventData(self.event_name)["CurrentEvent"] = ""
        state.SetEventDone(self.event_name, True)
        return output
        