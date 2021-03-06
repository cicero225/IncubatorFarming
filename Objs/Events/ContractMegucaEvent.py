import random
from Objs.Events.Event import *

class ContractMegucaEvent(Event):
    is_multistage_event = True
    last_stage = 1
    event_name = __name__
    event_display_name = event_name

    def __init__(self, meguca_city: MegucaCity):
        # See the Event class for documentation
        super().__init__(meguca_city)

    def Run(self, state, vote_result):
        potential = self.city.GetMegucasByTraits("potential")
        # it is important this order be deterministic
        potential.sort(key=lambda x: x.id)
        # Get the current event stage
        stage = state.GetEventStage(self.event_name)
        state.IncrementEventStage(self.event_name, self.last_stage)
        if stage == 0:
            output_text = "It is time for you to consider contracting a new magical girl. Here are the current girls with potential:"
            return EventResponse(self.event_name, self.event_display_name, output_text, [x.GetFullName() for x in potential] + ["Contract No One"])
        if stage == 1:
            if vote_result==len(potential):
                output_text = "We decided not to contract anyone, and move on."
                lost = self.city.PotentialDecay()     
                if lost:
                    output_text += f"\n\nIn the interim, it comes to your attention that some other girls have lost potential: {', '.join(l.GetFullName() for l in lost)}. This is unfortunate.\n\n"
                return EventResponse(self.event_name, self.event_display_name, output_text)
            new_meguca = potential[vote_result]
            # TODO: Maybe each function in meguca city should check and throw exceptions if necessary, and the class that manages the events handles them
            # TODO: That will mean we won't have to do exception handling in every event.
            meguca_name = new_meguca.GetFullName()
            meguca_wish = new_meguca.wish_type
            self.event_display_name = f"{meguca_name} contracted"

            energy_gain = self.city.ContractMeguca(new_meguca.id, state)

            output_text = self.GenerateOutputText(meguca_name, meguca_wish, energy_gain)

            lost = self.city.PotentialDecay()
            
            if lost:
                output_text += f"\n\nIn the interim, it comes to your attention that some other girls have lost potential: {', '.join(l.GetFullName() for l in lost)}. This is unfortunate.\n\n"
            
            return EventResponse(self.event_name, self.event_display_name, output_text)
    
    # TODO: Make it so they can turn down contracts sometimes?
    def GenerateOutputText(self, meguca_name, wish_type, energy_gain):
        # TODO: Maybe we should have different output text based on the girl's stats?
        # TODO: Also, I'm pretty sure that there is a better way to do this. I should do that later.

        first_paragraph = f"You approached {meguca_name} and offered the contract."

        second_paragraph_options = ["As your analysis suggested, she immediately consented.",
                                    "After some deliberation, she accepted the contract.",
                                    "After some time of thinking about it in secret, you approached her once again and she accepted the contract."]

        second_paragraph = random.choice(second_paragraph_options)

        third_paragraph = f"She wished for {wish_type}"

        fourth_paragraph = f"Entropy has been reduced! Gain {energy_gain} energy!"

        return "\n".join([first_paragraph, second_paragraph, third_paragraph, fourth_paragraph])




























