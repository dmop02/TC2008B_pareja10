from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from requests import post
import requests
from agent import *
import json
import random
import os
import networkx as nx
import matplotlib.pyplot as plt

class CityModel(Model):

    def __init__(self):

        self.city_graph = nx.DiGraph()
        self.total_cars = 0
        self.traffic_lights = []
        self.carsInDestination = 0
        self.step_count = 0
        dataDictionary = json.load(open("Server/city_files/mapDictionary.json"))
        
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
                    if col in ["v", "^", ">", "<", "E", "F", "G", "H"]:
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
        
        
        self.running = True
        self.num_agents = 0
        self.generateGraph()

    def generateCars(self, num_agents):
        """Generate N cars at random locations."""
        spawn_points = []

        
        allCorners = [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]
        for corner in allCorners:
            spawn_points.append(corner)

        
        if self.schedule.steps % 3 == 0:
            for _ in range(num_agents):
                spawn_point = self.random.choice([(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)])
                spawn_points.append(spawn_point)

        for spawn_point in spawn_points:
            i = 1
            # print(f"Spawning car at {spawn_point}")
            agent = Car(self.total_cars, self, self.getDestinations())
            self.grid.place_agent(agent, spawn_point)
            self.schedule.add(agent)
            self.total_cars += 1
            i += 1

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
        self.carsInDestination += 1
        


    def get_road_direction(self, x, y):
        possible_roads = self.grid.get_neighbors((x, y), moore=True, include_center=True, radius=1)
        for road in possible_roads:
            if isinstance(road, Road):
                return road.direction

        return "Undefined"
 

    def isPosValid(self, x, y):
        
        return 0 <= x < self.width and 0 <= y < self.height and (
            any(isinstance(agent, (Road, Traffic_Light, Destination)) for agent in self.grid.get_cell_list_contents((x, y)))
        )

    def add_traffic_light_edges(self, x, y, directions):
        
        for direction_name, (dx, dy) in directions.items():
            adjacent_x, adjacent_y = x + dx, y + dy
            if self.isPosValid(adjacent_x, adjacent_y) and any(isinstance(agent, Road) for agent in self.grid.get_cell_list_contents((adjacent_x, adjacent_y))):
                adjacent_agents = self.grid.get_cell_list_contents((adjacent_x, adjacent_y))
                road_agent = next((agent for agent in adjacent_agents if isinstance(agent, Road)), None)
                if road_agent:
                    if self.aligning_directions(road_agent, x, y, adjacent_x, adjacent_y):
                        self.city_graph.add_edge((adjacent_x, adjacent_y), (x, y), weight=self.calculate_edge_weight(adjacent_x, adjacent_y, x, y))
                    else:
                        self.city_graph.add_edge((x, y), (adjacent_x, adjacent_y), weight=self.calculate_edge_weight(x, y, adjacent_x, adjacent_y))
                        
    def aligning_directions(self, road_agent, tl_x, tl_y, road_x, road_y):
        
        if road_agent.direction == "Up" and road_y < tl_y:
            return True
        if road_agent.direction == "Down" and road_y > tl_y:
            return True
        if road_agent.direction == "Left" and road_x > tl_x:
            return True
        if road_agent.direction == "Right" and road_x < tl_x:
            return True
        return False

    def calculate_edge_weight(self, x, y, nx, ny):
        base_weight = 1
        next_agents = self.grid.get_cell_list_contents((nx, ny))
        if any(isinstance(agent, Traffic_Light) and agent.state for agent in next_agents):
            return base_weight * 5
        return base_weight
    
    def generateGraph(self):
        
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        diagonal_directions = {
            'Right': [('Right', 'Up'), ('Right', 'Down')],
            'Up': [('Up', 'Right'), ('Up', 'Left')],
            'Left': [('Left', 'Up'), ('Left', 'Down')],
            'Down': [('Down', 'Right'), ('Down', 'Left')]
        }

        for x in range(self.width):
            for y in range(self.height):
                agents = self.grid.get_cell_list_contents((x, y))
                if any(isinstance(agent, Destination) for agent in agents):
                    self.destination_edges(x, y, directions)
                elif any(isinstance(agent, Road) for agent in agents):
                    road_agent = next((agent for agent in agents if isinstance(agent, Road)), None)
                    if road_agent:
                        self.road_edges(x, y, road_agent, directions, diagonal_directions)
                elif any(isinstance(agent, Traffic_Light) for agent in agents):
                    self.add_traffic_light_edges(x, y, directions)
    
    def destination_edges(self, x, y, directions):
        
        for direction in directions.values():
            dx, dy = direction
            nx, ny = x + dx, y + dy
            if self.isPosValid(nx, ny) and any(isinstance(agent, Road) for agent in self.grid.get_cell_list_contents((nx, ny))):
                weight = self.calculate_edge_weight(x, y, nx, ny)
                self.city_graph.add_edge((nx, ny), (x, y), weight=weight)

    def road_edges(self, x, y, road_agent, directions, diagonal_directions):
        road_directions = road_agent.direction if isinstance(road_agent.direction, list) else [road_agent.direction]
        for direction in road_directions:
            dx, dy = directions[direction]
            nx, ny = x + dx, y + dy
            if self.isPosValid(nx, ny) and not any(isinstance(agent, Traffic_Light) for agent in self.grid.get_cell_list_contents((nx, ny))):
                weight = self.calculate_edge_weight(x, y, nx, ny)
                self.city_graph.add_edge((x, y), (nx, ny), weight=weight) 
                if direction in diagonal_directions: 
                    for diag in diagonal_directions[direction]:
                        ddx, ddy = (directions[diag[0]][0] + directions[diag[1]][0], directions[diag[0]][1] + directions[diag[1]][1])
                        nnx, nny = x + ddx, y + ddy
                        if self.isPosValid(nnx, nny) and not any(isinstance(agent, Traffic_Light) for agent in self.grid.get_cell_list_contents((nnx, nny))):
                            self.city_graph.add_edge((x, y), (nnx, nny), weight=weight * 3)
                            
    
    
    def weightEdges(self, x, y, nx, ny):
        
        base_weight = 1
        next_agents = self.grid.get_cell_list_contents((nx, ny))
        if any(isinstance(agent, Traffic_Light) and agent.state == "on" for agent in next_agents):
            return base_weight * 10
        return base_weight

    def step(self):
        """
        Avanza un paso en la simulación.
        """
        self.schedule.step()

        if self.schedule.steps == 1:
            self.generateCars(4)
            self.generateGraph()
        elif self.schedule.steps % 5 == 0:
            self.generateCars(2)
            self.generateGraph()

    