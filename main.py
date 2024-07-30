import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Set up the display window
screen = pygame.display.set_mode((1600, 600))
pygame.display.set_caption('Pygame Window')

# Define the boundaries of the robot area
LEFT_BOUNDARY = 0
RIGHT_BOUNDARY = 800
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 600

# Define the radius of the agent
AGENT_RADIUS = 20

class Agent:
    def __init__(self, x, y, direction, num_lidar_beams=720):
        self.x = x
        self.y = y
        self.direction = direction  # in degrees
        self.linear_speed = 0.1
        self.angular_speed = 0.1
        self.lidar_max_range = 10
        self.lidar_angles = [i * (360 / num_lidar_beams) for i in range(num_lidar_beams)]
        self.lidar_ranges = []
        self.bump_sensor = False
    
    def draw(self, screen):
        # Draw the circle
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), AGENT_RADIUS)
        
        # Calculate the end point of the arrow
        end_x = self.x + AGENT_RADIUS * math.cos(math.radians(self.direction))
        end_y = self.y - AGENT_RADIUS * math.sin(math.radians(self.direction))
        
        # Draw the arrow
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)
    
    def detect_collision(self, move_forward=True):
        # Calculate the next position
        if move_forward:
            next_x = self.x + self.linear_speed * math.cos(math.radians(self.direction))
            next_y = self.y - self.linear_speed * math.sin(math.radians(self.direction))
        else:
            next_x = self.x - self.linear_speed * math.cos(math.radians(self.direction))
            next_y = self.y + self.linear_speed * math.sin(math.radians(self.direction))

        # Check if the next position is within the boundaries considering the radius of the agent
        if (LEFT_BOUNDARY + AGENT_RADIUS <= next_x <= RIGHT_BOUNDARY - AGENT_RADIUS and
            TOP_BOUNDARY + AGENT_RADIUS <= next_y <= BOTTOM_BOUNDARY - AGENT_RADIUS):
            return False
        return True
    
    def move_forward(self):
        if not self.detect_collision(move_forward=True):
            self.x += self.linear_speed * math.cos(math.radians(self.direction))
            self.y -= self.linear_speed * math.sin(math.radians(self.direction))
            self.bump_sensor = False
        else:
            self.bump_sensor = True
    
    def move_backward(self):
        if not self.detect_collision(move_forward=False):
            self.x -= self.linear_speed * math.cos(math.radians(self.direction))
            self.y += self.linear_speed * math.sin(math.radians(self.direction))
            self.bump_sensor = False
        else:
            self.bump_sensor = True
    
    def rotate_left(self):
        self.direction = (self.direction + self.angular_speed) % 360
        self.bump_sensor = False
    
    def rotate_right(self):
        self.direction = (self.direction - self.angular_speed) % 360
        self.bump_sensor = False
    
    def handle_move_keys(self, keys):
        if keys[pygame.K_LEFT]:
            self.rotate_left()
        if keys[pygame.K_RIGHT]:
            self.rotate_right()
        if keys[pygame.K_UP]:
            self.move_forward()
        if keys[pygame.K_DOWN]:
            self.move_backward()

# Create an agent instance
agent = Agent(400, 300, 0)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    # Get the state of all keyboard buttons
    keys = pygame.key.get_pressed()
    
    # Handle agent's movement
    agent.handle_move_keys(keys)

    # Fill the screen with a white color
    screen.fill((255, 255, 255))

    # Draw the left half as the navigation area
    pygame.draw.rect(screen, (200, 200, 200), (LEFT_BOUNDARY, TOP_BOUNDARY, RIGHT_BOUNDARY - LEFT_BOUNDARY, BOTTOM_BOUNDARY - TOP_BOUNDARY))

    # Draw the agent
    agent.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()