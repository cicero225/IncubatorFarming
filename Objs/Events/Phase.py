from Objs.Utils.GlobalDefines import *
from Objs.Event.Events import Event
from typing import List

"""
A sort of Event metaclass, Phase represents any given phase of a game, containing knowledge of
which events to run and call, probability selection, and most of the other logic between events.

Like events, it needs to be able to run from any intermediate substage (or subevent). Phases can also be nested within themselves - after all, it is a subclass of Event! As such, it is intended as a flexible
representation of high-order event ordering.

Phase itself is also meant to be inherited from. It's a bit sparse, but is to some degree bookkeeping.
"""

class Phase(Event):
    def __init__(self, meguca_city: MegucaCity, is_multistage_event: bool, event_display_name: str,
                 valid_events: Dict[str, type]):
        super().__init__(self, meguca_city, is_multistage_event, event_display_name)
        self.valid_events = valid_events
        
    def RunEvent(self, event_name: str, state):
        # No need to actually make the event instance until we need it. This saves memory and initial
        # loading time, especially if we have a lot of events, considering we only ever need to initialize
        # at most one event.
        # Personal note: I wouldn't ordinarily bother, and would consider making each event a singleton class,
        # but there's a chance the bot ends up running on a raspberry pi.
        return self.valid_events[event_name](self.meguca_city, event_display_name=event_name).Run(state)
        
    # We still don't override Run, letting the concrete derived class deal with that.