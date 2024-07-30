import pygame
import sys
from agent import Agent
from wall import Wall
from button import Button
from colors import *

# Initialize pygame
pygame.init()

# Set up the display window
screen = pygame.display.set_mode((1600, 600))
pygame.display.set_caption('Simulation Window')

# Define the boundaries of the robot area
LEFT_BOUNDARY = 0
RIGHT_BOUNDARY = 800
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 600

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