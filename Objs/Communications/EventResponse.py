from typing import Tuple, List
import datetime


class EventResponse:

    def __init__(self, event_name: str,
                 event_display_name: str,
                 output_text: List[str],
                 voteable_options: Tuple[str] = (),
                 event_sub_index: int = 0):
        """
        Sets up an event response, which will be sent and displayed to the players

        :param event_name: The name of the event.
        :param event_display_name: The name of the event to display to the players, which could be different from the internal event name.
        :param output_text: Multi-paragraph text of the
        :param voteable_options: A tuple of strings, which will be displayed to the users as votable options
        :param event_sub_index: If the event has multiple stages, it's the current stage you are in.
        """

        self.event_name = event_name
        self.event_display_name = event_display_name
        self.event_sub_index = event_sub_index
        self.output_text = output_text
        self.voteable_options = voteable_options

        # Automatically generate timestamp
        self.timestamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

    # Quick hack. Do better job later maybe.
    def __repr__(self):
        return self.__dict__.__repr__()


































