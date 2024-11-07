from controller import Controller
from agent import Agent


class ControllerBasic(Controller):
    def __init__(self, model, agent: Agent):
        super().__init__(model, agent)
        self.move = None

    def handle_input(self):
        # print(f'bump sensor {self.agent.bump_sensor}')
        # print(f'lidar ranges {self.agent.lidar_ranges}')
        # print(f'position {self.agent.x,self.agent.y}, direction {self.agent.direction}')
        if self.agent.bump_sensor:
            self.move = "left"
        else:
            self.move = "forward"

    def move_agent(self):
        if not self.running:
            return

        if self.move == "left":
            self.agent.rotate_left()
        elif self.move == "forward":
            self.agent.try_move(move_forward=True)
