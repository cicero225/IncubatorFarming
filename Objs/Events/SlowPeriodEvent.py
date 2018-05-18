import random

from Objs.Events.Event import *

class SlowPeriodEvent(Event):
    base_weight = 2.0
    stat_modifiers = {}
    is_multistage_event = True
    last_stage = 1
    event_name = __name__
    event_display_name = event_name
    meguca_weights = {}

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city)
    
    @classmethod  # It is important for memory savings that this be a class method
    def GetValidMegucas(cls, city, state):
        return city.GetMegucasByTraits("contracted") + city.GetMegucasByTraits("potential")

    def Run(self, state, vote_result=None):
        stage = state.GetEventStage(self.event_name)
        state.IncrementEventStage(self.event_name, self.last_stage)
        list_valid = self.GetValidMegucas(self.city, state)
        if not list_valid:
            # For random events, returning None as the text implies the event was not valid.
            return EventResponse(self.event_name, self.event_display_name, None)
        if stage == 0:
            choices = [stat for stat in MEGUCA_STATS if not state.CheckSensorIsMax(stat)]
            if not choices:
                event_text = f"It is a quiet period in the city. With little to do, you spend some time grooming your fur to improve appearance for the next potential contract."
                # We deliberately increment _again_, to reset the event.
                state.IncrementEventStage(self.event_name, self.last_stage)
                return EventResponse(self.event_name, self.event_display_name, output_text)
            # select 3 choices as the options
            random.shuffle(choices)
            chosen = choices[0:min(3, len(choices))]
            state.GetEventData(self.event_name)["choices"] = chosen
            output_text = "It is a quiet period in the city, and you have the option of what to do with your time."
            vote_text_dict = {
                "potential": "Study the impact of a magical girl on human society",
                "neuroticism": "Observe unstable emotional behavior",
                "friendships": "Observe a girl's interaction with her friends",
                "gullibility": "Observe a girl going shopping",
                "secretiveness": "Observe a girl trying to hide information",
                "bravery": "Observe a girl taking on some bullies",
                "cleverness": "Observe a girl taking a test",
                "narcissism": "Observe a girl decorating herself with ornaments",
                "aggression": "Observe a girl attacking her enemies"}
            return EventResponse(self.event_name, self.event_display_name, output_text, [vote_text_dict[x] for x in chosen])
        elif stage == 1:           
            meguca = random.choice(list_valid)
            # Random int
            event_choice = state.GetEventData(self.event_name)["choices"][vote_result]
            # TODO: Add wish type?  
            if event_choice == "cleverness":
                event_text = f"You observe {meguca.GetFullName()} taking a school test, and learn a little about human cleverness."
                state.ChangeSensors("cleverness", 1)
            elif event_choice == "bravery":
                event_text = f"You observe {meguca.GetFullName()} taking on some bullies, learning about human bravery."
                state.ChangeSensors("bravery", 1)
            elif event_choice == "aggression":
                event_text = f"You observe {meguca.GetFullName()} fighting an enemy, learning about human aggression."
                state.ChangeSensors("aggression", 1)
            elif event_choice == "potential":
                event_text = f"You study {meguca.GetFullName()}'s impact on human development, learning about the origins of potential."
                state.ChangeSensors("potential", 1)
            elif event_choice == "neuroticism":
                event_text = f"You observe the unstable emotional behavior of {meguca.GetFullName()}, learning about human neuroticism."
                state.ChangeSensors("neuroticism", 1)
            elif event_choice == "friendships":
                event_text = f"You observe {meguca.GetFullName()} interacting with her friends, learning about human friendship."
                state.ChangeSensors("friendships", 1)
            elif event_choice == "gullibility":
                event_text = f"You observe {meguca.GetFullName()} purchasing an item from a merchant, learning about human gullibility."
                state.ChangeSensors("gullibility", 1)
            elif event_choice == "secretiveness":
                event_text = f"You observe {meguca.GetFullName()} trying to hide information, learning about human secretiveness."
                state.ChangeSensors("secretiveness", 1)
            elif event_choice == "narcissism":
                event_text = f"You observe {meguca.GetFullName()} putting on makeup, learning about human narcissism."
                state.ChangeSensors("narcissism", 1)
            return EventResponse(self.event_name, self.event_display_name, event_text)