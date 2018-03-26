from Objs.MegucaCity.MegucaCity import MegucaCity
from Objs.Communications.EventResponse import *

class Event:

    def __init__(self, meguca_city: MegucaCity, is_multistage_event: bool,  event_display_name: str= None):
        """
        Initializes an Event.
        This class is not meant to be used, only inherited from.
        :param meguca_city: The MegucaCity instance used by the game. The event requires it to
                            execute changes to the state of the game.
        :param is_multistage_event: A boolean value of if the event is multistage or not.
        :param event_display_name: The display name of the event. If None then the name of the event class will
                                   be used
        """

        # We always use the name of the class as the name of the event
        self.event_name = self.__class__.__name__

        self.city = meguca_city
        self.is_multistage_event = is_multistage_event

        if event_display_name is None:
            event_display_name = self.event_name
        self.event_display_name = event_display_name



























