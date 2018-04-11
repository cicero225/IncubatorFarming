import random
from Objs.Events.Event import *


class StartGameEvent(Event):
    CITIES = ["Mitakihara", "Shanghai", "Tokyo", "Paris", "London", "New York"]

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city, False, "StartGameEvent")

    def Run(self, state, vote_result):
        start_text = f"Welcome to the city of {random.choice(self.CITIES)}, Incubator! The hivemind has high expectations of you. Go forth and recruit magical girls to save the universe, but be wary of the pitfalls that await a reckless Incubator."
        return EventResponse(self.event_name, self.event_display_name, start_text)