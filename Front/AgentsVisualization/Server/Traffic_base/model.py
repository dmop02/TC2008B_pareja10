from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from Traffic_base.agent import *
import json
import os

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Define the file path
        dataDictionary = json.load(open("static/city_files/mapDictionary.json"))


        self.traffic_lights = []
        self.total_cars = 0

        # Load the map file. The map file is a text file where each character represents an agent.
        with open("static/city_files/2022_base.txt") as baseFile:
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
        spawn_points = [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]

        for spawn_point in spawn_points:
            print("spawn point: ", spawn_point)
            print("destinations: ", self.getDestinations())
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
        if (self.schedule.steps -1) % 10 == 0:
            self.generateCars(4)

        

