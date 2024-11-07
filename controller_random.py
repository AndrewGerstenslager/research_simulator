from controller import Controller
from agent import Agent
import random


class ControllerRandom(Controller):
    def __init__(self, model, agent: Agent):
        super().__init__(model, agent)
        self.move = "same"
        self.choices = [direction for direction in range(0, 360, 45)]
        self.goal_direction = None

    def turn_direction(self, current_angle, goal_angle):
        # Calculate the difference between the goal angle and the current angle
        angle_diff = (goal_angle - current_angle) % 360
        if angle_diff > 180:
            angle_diff -= 360

        # Determine if left or right turn is needed
        if angle_diff > 0:
            return "left"
        elif angle_diff < 0:
            return "right"
        else:
            return "same"

    def change_course(self, epsilon=0.05):
        if random.random() > epsilon:
            return

        direction = self.agent.direction
        if random.random() > 0.5:
            goal = self.choices[self.choices.index(direction) - 1]
        else:
            goal = self.choices[self.choices.index(direction) - 7]

        self.goal_direction = goal
        self.move = self.turn_direction(direction, goal)

    def handle_input(self):
        if self.agent.bump_sensor:
            direction = self.agent.direction
            goal = random.choice(self.choices)
            self.goal_direction = goal
            self.move = self.turn_direction(direction, goal)
        else:
            self.move = "same"

    def move_agent(self):
        if not self.running:
            return

        if self.agent.bump_sensor or (
            self.goal_direction is not None
            and self.agent.direction != self.goal_direction
        ):
            direction = self.agent.direction
            self.move = self.turn_direction(direction, self.goal_direction)

            if self.move == "left":
                self.agent.rotate_left()
            elif self.move == "right":
                self.agent.rotate_right()

            # Check if the goal direction is reached
            if direction == self.goal_direction:
                self.goal_direction = None
                self.move = "same"
        else:
            self.handle_input()

            if self.move == "same":
                self.agent.try_move(move_forward=True)
                self.change_course()  # Chance to deviate direction
