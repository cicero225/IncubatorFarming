import random

from Objs.Events.Event import *

class SlowPeriodEvent(Event):
    base_weight = 2.0
    stat_modifiers = {}
    is_multistage_event = False
    event_name = __name__
    event_display_name = event_name

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city)
    
    @classmethod  # It is important for memory savings that this be a class method
    def GetValidMegucas(cls, city, state):
        return city.GetMegucasByTraits("contracted") + city.GetMegucasByTraits("potential")

    def Run(self, state, vote_result=None):
        # Search for a meguca with friendships = 1
        list_valid = self.GetValidMegucas(self.city, state)
        if not list_valid:
            # For random events, returning None as the text implies the event was not valid.
            return EventResponse(self.event_name, self.event_display_name, None)
        meguca = random.choice(list_valid)
        # Random int
        event_choice = random.choice([stat for stat in MEGUCA_STATS if not state.CheckSensorIsMax(stat)])
        # TODO: Make this a vote instead on what sensor they want to improve.
        # TODO: Add wish type?  
        if event_choice == "cleverness":
            event_text = f"It is a quiet period in the city, and you observe {meguca.GetFullName()} taking a school test, and learn a little about human cleverness."
            state.ChangeSensors("cleverness", 1)
        elif event_choice == "bravery":
            event_text = f"It is a quiet period in the city, and you observe {meguca.GetFullName()} taking on some bullies, learning about human bravery."
            state.ChangeSensors("bravery", 1)
        elif event_choice == "aggression":
            event_text = f"It is a quiet period in the city, and you observe {meguca.GetFullName()} fighting an enemy, learning about human aggression."
            state.ChangeSensors("aggression", 1)
        elif event_choice == "potential":
            event_text = f"It is a quiet period in the city, and you study {meguca.GetFullName()}'s impact on human development, learning about the origins of potential."
            state.ChangeSensors("potential", 1)
        elif event_choice == "neuroticism":
            event_text = f"It is a quiet period in the city, and you observe the unstable emotional behavior of {meguca.GetFullName()}'s, learning about human neuroticism."
            state.ChangeSensors("neuroticism", 1)
        elif event_choice == "friendships":
            event_text = f"It is a quiet period in the city, and you observe {meguca.GetFullName()} interacting with her friends, learning about human friendship."
            state.ChangeSensors("friendships", 1)
        elif event_choice == "gullibility":
            event_text = f"It is a quiet period in the city, and you observe {meguca.GetFullName()} purchasing an item from a merchant, learning about human gullibility."
            state.ChangeSensors("gullibility", 1)
        elif event_choice == "secretiveness":
            event_text = f"It is a quiet period in the city, and you observe {meguca.GetFullName()} trying to hide information, learning about human secretiveness."
            state.ChangeSensors("secretiveness", 1)
        elif event_choice == "narcissism":
            event_text = f"It is a quiet period in the city, and you observe {meguca.GetFullName()} putting on makeup, learning about human narcissism."
            state.ChangeSensors("narcissism", 1)   
        else:
            event_text = f"It is a quiet period in the city. With little to do, you spend some time grooming your fur to improve appearance for the next potential contract."
        return EventResponse(self.event_name, self.event_display_name, event_text)