from controllers.controller import Controller
from agent import Agent
import random

class RandomController(Controller):
    def __init__(self, model, agent : Agent):
        super().__init__(model, agent)
        self.move = None 
        self.choices = [direction for direction in range(0, 360, 45)]

    def handle_input(self):
        if self.agent.bump_sensor:
            self.move = random.choice(self.choices)
        else:
            self.move = self.agent.direction

    def move_agent(self):
        if not self.running: return

        rotation = self.agent.direction
        while rotation != self.move:
            self.agent.rotate_left()
            rotation = self.agent.direction
        
        self.agent.move_forward()

