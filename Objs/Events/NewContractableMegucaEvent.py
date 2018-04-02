from Objs.Events.Event import *

class NewContractableMegucaEvent(Event):
    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city, False, "NewContractableMegucaEvent")

    # TODO: Put the proper text here.
    def Run(self, state):
        new_meguca = self.city.NewSensorMeguca(state.targets, state.sensors)
        state.GetEventData(self.event_name)["new_meguca_id"] = new_meguca.id
        return EventResponse(self.event_name, self.event_display_name, "PLACEHOLDER")