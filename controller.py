from abc import ABC, abstractmethod
from agent import Agent

class Controller(ABC):
    def __init__(self, model, agent : Agent):
        self.model = model
        self.agent = agent
        self.running = False

    @abstractmethod
    def handle_input(self):
        pass
    
    @abstractmethod
    def move_agent(self):
        pass

