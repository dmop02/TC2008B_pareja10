from mesa import Agent
import random
import networkx as nx
import heapq

def heuristic(a, b):
    """
    Calculates the Manhattan distance between two points.
    Args:
        a: First point
        b: Second point
    Returns:
        Manhattan distance between the two points
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(graph, start, goal, path_clear):
    """
    A* search algorithm.
    Args:
        graph: The graph where the search will be performed
        start: Starting point
        goal: Goal point
        path_clear: Function to check if the path is clear
    Returns:
        The path to be followed
    """
    print(f"Starting A* search from {start} to {goal}")
    
    open_set = []  # Priority queue for nodes to be evaluated
    heapq.heappush(open_set, (0, start))
    
    predecessors = {start: None}  # Dictionary to store the parent of each node
    g_score = {start: 0}  # Cost from start along best known path
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        print(f"Checking cell: {current}")

        if current == goal:
            break

        for neighbor in graph.get_neighborhood(current, moore=False, include_center=False):
            if not path_clear(current, neighbor):
                continue

            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(goal, neighbor)
                heapq.heappush(open_set, (f_score, neighbor))
                predecessors[neighbor] = current

    path = {}
    current_node = goal
    while current_node != start:
        if current_node in predecessors:
            previous_node = predecessors[current_node]
            path[previous_node] = current_node
            current_node = previous_node
        else:
            print("No path found")
            return {}

    print(f"Path found: {path}")
    return path


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, start, destination):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """

        super().__init__(unique_id, model)

        self.start = start
        self.destination = destination
        self.path = None

    def getPath(self):
        self.path = self.find_path()

    def isMoveAllowed(self, currentPos, nextPos, roadDir):
        dx = nextPos[0] - currentPos[0]  # Change in x
        dy = nextPos[1] - currentPos[1]  # Change in y

        # Define a dictionary to map road directions to movement conditions
        direction_conditions = {
            "Right": dx != -1,
            "Left": dx != 1,
            "Up": dy != -1,
            "Down": dy != 1,
        }

        # Use the dictionary to check the movement condition based on road direction
        return direction_conditions.get(roadDir, False)
        
    def find_path(self):
        if self.destination:
            def path_clear(currentPos, nextPos):
                content = self.model.grid.get_cell_list_contents([nextPos])
                if any (isinstance(agent, Obstacle) for agent in content):
                    return False
                if any(isinstance(agent, (Road, Traffic_Light, Destination)) for agent in content):
                    roadAgents = [agent for agent in content if isinstance(agent, Road)]
                    if roadAgents:
                        roadAgent = roadAgents[0]
                        return self.isMoveAllowed(currentPos, nextPos, roadAgent.direction)
                    return True
                return False
            return a_star_search(self.model.grid, self.start, self.destination, path_clear)
        return None
    
    def calculateDirection(self, currentPos, nextPos):
        direction_mapping = {(1, 0): "Right", (-1, 0): "Left", (0, -1): "Up", (0, 1): "Down"} # Diccionario para mapear los cambios en x y y a direcciones
        dx = nextPos[0] - currentPos[0] # Se calcula el cambio en x 
        dy = nextPos[1] - currentPos[1] # Se calcula el cambio en y 
        return direction_mapping.get((dx, dy), None)

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        if self.path and self.pos in self.path: # If the path is set and the current position is in the path,
            if isinstance(self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]], list):
                # Itera sobre los agentes en la lista

                for agent_in_cell in self.model.grid[self.path.get(self.pos)[0]][self.path.get(self.pos)[1]]:
                    if type(agent_in_cell) == Car:
                        next_pos = self.pos
                    elif type(agent_in_cell) == Traffic_Light:
                        if agent_in_cell.state == False:
                            next_pos = self.pos
                        else:
                            next_pos = self.path.get(self.pos) # Get the next position
                    else:
                        next_pos = self.path.get(self.pos) # Get the next position
            
            if next_pos is not None: # If the next position is not None,
                self.model.grid.move_agent(self, next_pos) # Move the agent to the next position
                self.direction = self.calculateDirection(self.pos, next_pos) # Get the direction the agent should face
                if next_pos == self.destination: # If the destination is reached,
                    print(f"Car {self.unique_id} reached destination {self.destination}") 
                    self.model.remove_car(self) # Remove the car from the model
            else: # If the next position is None,
                print("No valid next position found.")
    
    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """

        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass

