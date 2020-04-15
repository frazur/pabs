import math

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule, CanvasGrid
from mesa.visualization.modules import TextElement
from .model import PabsModel, State, PabsAgent, number_infected, number_dead, number_susceptible, number_resistant


def pabs_portrayal(agent: PabsAgent):
    '''
     Portrayal Method for canvas
     '''
    if agent is None:
        return
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}

    if agent.state == State.INFECTED:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
        portrayal["r"] = 1
    elif agent.state == State.RESISTANT:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.8
    elif agent.state == State.SUSCEPTIBLE:
        portrayal["Color"] = "green"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.8
    else:
        portrayal["Color"] = "black"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.8
    return portrayal


grid = CanvasGrid(pabs_portrayal, 70, 70, 500, 500)
chart = ChartModule([{'Label': 'Infected', 'Color': '#FF0000'},
                     {'Label': 'Susceptible', 'Color': '#008000'},
                     {'Label': 'Resistant', 'Color': 'blue'},
                     {'Label': 'Dead', 'Color': 'black'}
                     ])


class PabsTextElement(TextElement):
    def render(self, model):
        ratio = model.resistant_susceptible_ratio()
        ratio_text = '&infin;' if ratio is math.inf else '{0:.2f}'.format(ratio)
        infected_text = str(number_infected(model))
        dead_text = str(number_dead(model))
        survived_text = str(number_infected(model) + number_susceptible(model) + number_resistant(model))
        return "Resistant/Susceptible Ratio: {}<br>" \
               "Infected Remaining: {}<br>" \
               "Total deads: {}<br>" \
               "Total survived: {}".format(ratio_text,
                                           infected_text,
                                           dead_text,
                                           survived_text)


model_params = {
    'num_agents': UserSettableParameter('slider', 'Number of agents', 1000, 10, 2500, 1,
                                        description='Choose how many agents to include in the model'),
    'width': 70,
    'height': 70,
    'initial_outbreak_size': UserSettableParameter('choice', 'Initial Outbreak Size', 0.01,
                                                   choices=[0.001, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5],
                                                   description='Initial Outbreak Size (% of population)'),
    'virus_spread_chance': UserSettableParameter('slider', 'Virus Spread Chance', 0.85, 0.0, 1.0, 0.05,
                                                 description='Probability that susceptible neighbor will be infected'),
    'virus_check_frequency': UserSettableParameter('slider', 'Virus Check Frequency', 0.4, 0.0, 1.0, 0.1,
                                                   description='Frequency the nodes check whether they are infected by '
                                                               'a virus'),
    'recovery_chance': UserSettableParameter('slider', 'Recovery Chance', 0.3, 0.0, 1.0, 0.1,
                                             description='Probability that the virus will be removed'),
    'gain_resistance_chance': UserSettableParameter('slider', 'Gain Resistance Chance', 0.5, 0.0, 1.0, 0.1,
                                                    description='Probability that a recovered agent will become '
                                                                'resistant to this virus in the future'),
    'min_infection_duration': UserSettableParameter('slider', 'Infection duration (ticks)', 5, 0, 15, 1,
                                                    description='How many ticks min infection'),
    'death_chance': UserSettableParameter('slider', 'Death chance', 0.02, 0.0, 1.0, 0.01,
                                          description='Probability that an agent will die if infected'),
    'resistance_duration': UserSettableParameter('slider', 'Resistance duration (ticks, -1 forever)', -1, -1, 100, 1,
                                                 description='How many ticks resistance lasts (-1 is forever)'),
    'movers': UserSettableParameter('slider', 'People who can move around', 1.0, 0.0, 1.0, 0.1,
                                    description='Probability that an agent will move')
}

server = ModularServer(PabsModel, [grid, PabsTextElement(), chart], 'Pandemic Agent Based Simulation', model_params)
server.port = 8521
