from Objs.Communications.EventResponse import *
from Objs.Utils.GlobalDefines import *
from Objs.Events.Event import Event
from Objs.MegucaCity.MegucaCity import MegucaCity
from typing import List, Dict

"""
A sort of Event metaclass, Phase represents any given phase of a game, containing knowledge of
which events to run and call, probability selection, and most of the other logic between events.

Like events, it needs to be able to run from any intermediate substage (or subevent). Phases can also be nested within themselves - after all, it is a subclass of Event! As such, it is intended as a flexible
representation of high-order event ordering.

Phase itself is also meant to be inherited from. It's a bit sparse, but is to some degree bookkeeping.
"""

class Phase(Event):
    def __init__(self, meguca_city: MegucaCity, is_multistage_event: bool, event_display_name: str,
                 base_weight: float = 1.0, stat_modifiers: Dict[str, float] = {}, last_stage=0,
                 valid_events: Dict[str, type] = {}):
        super().__init__(meguca_city, is_multistage_event, event_display_name, base_weight,
        stat_modifiers, last_stage)
        self.valid_events = valid_events
        
    def RunEvent(self, event_name: str, state, vote_result):
        # No need to actually make the event instance until we need it. This saves memory and initial
        # loading time, especially if we have a lot of events, considering we only ever need to initialize
        # at most one event.
        # Personal note: I wouldn't ordinarily bother, and would consider making each event a singleton class,
        # but there's a chance the bot ends up running on a raspberry pi.
        event_instance = self.valid_events[event_name](self.city)
        output = event_instance.Run(state, vote_result)
        if self.CheckIfEventDone(state, event_instance.event_name):
            # if event has only 1 stage, then new_stage is always 0 and we always increment.
            # if event has >1 stage, then if new_Stage is 0 event is done and we must increment.
            # Otherwise, do not increment.
            state.IncrementEventStage(self.event_name, self.last_stage)
        return output
        
    # We still don't override Run, letting the concrete derived class deal with that.
    
    @staticmethod
    def CheckIfEventDone(state, event_name):
        # Only run this after running the event once.
        # single-stage events have stage=0 but are always done.
        # multi-stage events are done if their stage have cycled around to 0
        return (state.GetEventStage(event_name) == 0)
    
    # Some simple utilities for common tasks.
    @staticmethod
    def CheckIfVote(output: EventResponse):
        return bool(output.votable_options)