from Objs.Utils.GlobalDefines import *
from Objs.Event.Events import Event

"""
A sort of Event metaclass, Phase represents any given phase of a game, containing knowledge of
which events to run and call, probability selection, and most of the other logic between events.

Like events, it needs to be able to run from any intermediate substage (or subevent). Phases can also be nested within themselves - after all, it is a subclass of Event! As such, it is intended as a flexible
representation of high-order event ordering.
"""
class Phase(Event):
    pass