import random

from Objs.Events.Event import *

# TODO: Make Random events their own base class to derive this from? Maybe...
class NotAfraidOfAnythingAnymoreEvent(Event):
    base_weight = 1.0
    stat_modifiers = {"friendships": -1}
    is_multistage_event = False
    event_name = __name__
    event_display_name = event_name

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city)
    
    @classmethod  # It is important for memory savings that this be a class method
    def GetValidMegucas(cls, city, state):
        return city.GetMegucasByTraits("contracted", valid_range={"friendships": (1,1)})

    def Run(self, state, vote_result=None):
        # Search for a meguca with friendships = 1
        list_valid = self.GetValidMegucas(self.city, state)
        if not list_valid:
            # For random events, returning None as the text implies the event was not valid.
            return EventResponse(self.event_name, self.event_display_name, None)
        meguca = random.choice(list_valid)
        # Get potential new friends
        list_valid_friends = self.city.GetMegucasByTraits("potential")
        valid_ids = set(x.id for x in list_valid_friends) - set(x.id for x in meguca.friends) - set(x.id for x in meguca.family)
        if not valid_ids:
            return EventResponse(self.event_name, self.event_display_name, None)
        new_friend = self.city.GetMegucaById(random.choice(list(valid_ids)))
        # Set bravery to 5, friendships to 2
        meguca.stats["bravery"] = 5
        meguca.stats["friendships"] = 2
        self.city.friends_tracker.Connect(meguca, new_friend)
        event_text = f"The lonely {meguca.GetFullName()} has made friends with {new_friend.GetFullName()} and says she isn't afraid of anything anymore! This strikes you as perhaps bad for her longevity."
        return EventResponse(self.event_name, self.event_display_name, event_text)