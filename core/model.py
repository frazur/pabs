import math
from enum import Enum

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid, MultiGrid


class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2
    DEAD = 3


def number_state(model, state):
    return sum([1 for a in model.agents if a.state is state])


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)


def number_dead(model):
    return number_state(model, State.DEAD)


def number_total(model):
    return number_dead(model) + number_resistant(model) + number_infected(model)



class PabsModel(Model):
    """Model your your pandemic"""

    def __init__(self, num_agents=10, width=10, height=10, initial_outbreak_size=0.1, virus_spread_chance=0.4,
                 virus_check_frequency=0.4, recovery_chance=0.3, gain_resistance_chance=0.5, min_infection_duration=5,
                 death_chance=0.5,
                 movers=0.1):
        self.agents = set()
        self.num_agents = num_agents
        self.width = width
        self.height = height
        self.grid = MultiGrid(height, width, True)
        self.schedule = RandomActivation(self)
        self.initial_outbreak_size = initial_outbreak_size if initial_outbreak_size <= 1.0 else 1.0
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.movers = movers
        self.death_chance = death_chance
        self.datacollector = DataCollector({"Infected": number_infected,
                                            "Susceptible": number_susceptible,
                                            "Resistant": number_resistant,
                                            "Dead": number_dead,
                                            "Total cases": number_total
                                            })

        # Create agents
        for i in range(self.num_agents):
            rn = self.random.random()
            if rn <= self.initial_outbreak_size:
                a = PabsAgent(i, self, State.INFECTED, self.virus_spread_chance, self.virus_check_frequency,
                              self.recovery_chance, self.gain_resistance_chance, min_infection_duration,
                              self.death_chance,
                              movable=False)
            else:
                a = PabsAgent(i, self, State.SUSCEPTIBLE, self.virus_spread_chance, self.virus_check_frequency,
                              self.recovery_chance, self.gain_resistance_chance, min_infection_duration,
                              self.death_chance,
                              movable=False)
            mrn = self.random.random()
            if mrn < movers:
                a.movable = True

            self.schedule.add(a)
            self.agents.add(a)
            # Add the agent to the node
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # # Infect some nodes
        # infected_nodes = self.random.sample(self., self.initial_outbreak_size)
        # for a in self.grid.get_cell_list_contents(infected_nodes):
        #     a.state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(self, State.SUSCEPTIBLE)
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class PabsAgent(Agent):
    def __init__(self, unique_id, model, initial_state,
                 virus_spread_chance,
                 virus_check_frequency,
                 recovery_chance,
                 gain_resistance_chance,
                 min_infection_duration,
                 death_chance,
                 movable=True):
        super().__init__(unique_id, model)

        self.state = initial_state

        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.death_chance = death_chance
        self.movable = movable
        self.min_infection_duration = min_infection_duration
        self.infected_eta = 0

    def move(self):
        if self.movable and self.state is not State.DEAD:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def try_to_survive(self):
        if self.random.random() <= 0.5 and self.random.random() < self.death_chance:
            self.state = State.DEAD
            return False
        return True

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        susceptible_neighbors = [agent for agent in neighbors_nodes if
                                 agent.state is State.SUSCEPTIBLE]
        for a in susceptible_neighbors:
            if self.random.random() < self.virus_spread_chance:
                a.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if self.infected_eta > self.min_infection_duration:
            if self.random.random() < self.recovery_chance:
                # Success
                self.state = State.SUSCEPTIBLE
                self.try_gain_resistance()
            else:
                # Failed
                self.state = State.INFECTED

    def try_check_situation(self):
        if self.random.random() < self.virus_check_frequency:
            # Checking...
            if self.state is State.INFECTED:
                self.try_remove_infection()

    def step(self):
        self.move()
        if self.state is State.INFECTED:
            self.infected_eta += 1
            if self.try_to_survive():
                self.try_to_infect_neighbors()
            self.try_check_situation()
