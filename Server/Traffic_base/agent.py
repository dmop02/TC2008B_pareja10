# Domingo Mora y Cristina González 
from mesa import Agent
import random
import networkx as nx

class Car(Agent):
    def __init__(self, unique_id, model, destination):
        """
        Crea un nuevo agente carro
        Args:
            unique_id: ID del agente
            model: Referencia al modelo
            destination: Destino del carro
        """
        super().__init__(unique_id, model)
        self.destination = destination
        self.direction = ""
        self.path = []  
        self.waiting = False  
        
    
    def calculatePath(self):
        """
        Método que calcula el camino más corto desde la posición actual del carro hasta su destino
        """
        start = self.pos
        goal = self.destination
        city_graph = self.model.city_graph # Se obtiene el grafo de la ciudad
        path = nx.shortest_path(city_graph, start, goal) # Se calcula el camino más corto usando Dijsktra
        path.pop(0) # Se elimina la posición actual del carro
        return path

    
    def isMoveAllowed(self, currentPos, nextPos):
        """
        Método que verifica si el carro puede moverse a la posición indicada
        """
        contents = self.model.grid.get_cell_list_contents([nextPos])

        for content in contents:
            if isinstance(content, Traffic_Light) and not content.state:
                return False
            elif isinstance(content, Car):
                return False

        return True

    def getCellAhead(self):
        """
        Método que obtiene la posición del carro que está adelante del carro actual
        """
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        direction = self.getDirection()

        if direction:
            dx, dy = directions[direction]
            aheadX, aheadY = self.pos[0] + dx, self.pos[1] + dy
            return aheadX, aheadY

        return None
    
    def getDirection(self):
        """
        Método que obtiene la dirección del carro
        """
        if self.path:
            dx = self.path[0][0] - self.pos[0]
            dy = self.path[0][1] - self.pos[1]
            if dx == 1:
                return 'Right'
            elif dx == -1:
                return 'Left'
            elif dy == 1:
                return 'Up'
            elif dy == -1:
                return 'Down'
    
    def recalculate(self, start = None, destination = None):
        """
        Método que recalcula el camino más corto desde la posición actual del carro hasta su destino
        Args:
            start: Posición inicial del carro
            destination: Destino del carro
        """
        self.pos = start if start else self.pos
        self.destination = destination if destination else self.destination

        try:
            self.path = self.calculatePath()
        except nx.NetworkXNoPath:
            self.path = []

    

    def handleLaneChange(self, start = None, destination = None):
        """
        Método que maneja el cambio de carril del carro
        """
        if random.random() < 0.5:
            self.direction = self.getDirection()
            cellAhead = self.getCellAhead()

            if cellAhead is not None:
                lane_change_step = cellAhead
                if self.model.isPosValid(*lane_change_step):

                    contents = self.model.grid.get_cell_list_contents([lane_change_step])
                    trafficLight = next((content for content in contents if isinstance(content, Traffic_Light)), None)
                    if trafficLight and not trafficLight.state:
                        return
                    neighborhood_cells = self.model.grid.get_neighborhood(lane_change_step, moore=True, include_center=True)
                    carsInAdjPos = sum(isinstance(c, Car) for cell in neighborhood_cells for c in self.model.grid.get_cell_list_contents([cell]))

                    if carsInAdjPos >= 3:
                        adjPositions = []
                        if self.direction == 'Up':
                            adjPositions = [(self.pos[0] - 1, self.pos[1] + 1), (self.pos[0] + 1, self.pos[1] + 1)]
                        elif self.direction == 'Down':
                            adjPositions = [(self.pos[0] - 1, self.pos[1] - 1), (self.pos[0] + 1, self.pos[1] - 1)]
                        elif self.direction == 'Left':
                            adjPositions = [(self.pos[0] - 1, self.pos[1] - 1), (self.pos[0] - 1, self.pos[1] + 1)]
                        elif self.direction == 'Right':
                            adjPositions = [(self.pos[0] + 1, self.pos[1] - 1), (self.pos[0] + 1, self.pos[1] + 1)]


                        possibleAdjPos = [(x, y) for x, y in adjPositions if self.model.isPosValid(x, y)]
                        
                        emptyAdjPos = possibleAdjPos
                        emptyAdjPos = [
                            pos for pos in possibleAdjPos 
                            if not any(isinstance(agent, (Car, Destination)) for agent in self.model.grid.get_cell_list_contents([pos]))
                        ]

                        if emptyAdjPos:
                            new_position = emptyAdjPos[0]
                            self.model.grid.move_agent(self, new_position)
                            self.recalculate(new_position, self.destination)
                            self.waiting = False
                            self.direction = self.getDirection()
                            
        if start or destination:
            self.recalculate(start, destination)

    
    def move(self):
        """ 
        Método que mueve el carro a la siguiente posición en su camino
        """
        
        self.handleLaneChange()

        if not self.path:
            self.path = self.calculatePath()

        if self.path:
            nextPos = self.path[0]

            if nextPos == self.destination:
                self.model.removeCar(self)
            else:
                self.direction = self.getDirection()
                if self.isMoveAllowed(self.pos, nextPos):
                    self.model.grid.move_agent(self, nextPos)
                    self.path.pop(0)
                else:
                    self.waiting = True

                    cellAhead = self.getCellAhead()

                    if cellAhead is not None:
                        next_cell = self.model.grid.get_cell_list_contents([cellAhead]) if self.model.isPosValid(*cellAhead) else []

                        if not self.isMoveAllowed(self.pos, cellAhead) or next_cell:
                            self.waiting = True


    def step(self):
        """
        Método que ejecuta el paso del modelo
        """
        self.move()


class Traffic_Light(Agent):
    """
    Agente semáforo
    """
    def __init__(self, unique_id, model, state=False, timeToChange=10):
        """
        Crea un nuevo agente semáforo
        Args:
            unique_id: ID del agente
            model: Referencia al modelo
            state: Estado del semáforo
            timeToChange: Tiempo en pasos de modelo para cambiar el estado del semáforo
        """
        super().__init__(unique_id, model)
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state


class Destination(Agent):
    """
    Agente destino
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Obstacle(Agent):
    """
    Agente obstáculo 
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Road(Agent):
    """
    Agente calle
    """
    def __init__(self, unique_id, model, direction="TrafficLight"):
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass