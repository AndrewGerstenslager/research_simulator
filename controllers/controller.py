from abc import ABC, abstractmethod

class Controller(ABC):
    def __init__(self, model, agent):
        self.model = model
        self.agent = agent
        self.running = False

    @abstractmethod
    def handle_input(self):
        pass
    
    @abstractmethod
    def move_agent(self):
        pass

