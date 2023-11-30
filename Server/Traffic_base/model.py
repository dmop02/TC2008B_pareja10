from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import os

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):
        

        # Define the file path
        dataDictionary = json.load(open("Server/city_files/mapDictionary.json"))


        self.traffic_lights = []
        self.total_cars = 0

        # Load the map file. The map file is a text file where each character represents an agent.
        with open("Server/city_files/2023_base.txt") as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)

        self.num_agents = N
        self.running = True
    def generateCars(self, num_agents):
        """ Generate N cars at random locations. """
        if self.schedule.steps == 0:
            # On the first step, initialize four cars at each corner
            spawn_points = [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]
        else:
            # On subsequent steps, initialize two cars at a random corner
            spawn_points = [self.random.choice([(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]) for _ in range(2)]

        for spawn_point in spawn_points:
            agent = Car(self.total_cars + 1, self, spawn_point, self.getDestinations())
            agent.getPath()
            self.grid.place_agent(agent, spawn_point)
            self.schedule.add(agent)
            self.total_cars += 1

           
        

    def getDestinations(self):
        destinations = []
        for agent in self.schedule.agents:
            if isinstance(agent, Destination):
                destinations.append(agent.pos)
        return self.random.choice(destinations)
    
    def remove_car(self, car):
        self.schedule.remove(car)
        self.grid.remove_agent(car)
        self.num_agents -= 1

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        current_step = self.schedule.steps - 1

        if current_step == 0:
            self.generateCars(4)
        
        if current_step % 3 == 0:
            self.generateCars(1)
        

