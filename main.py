import pygame
import sys
import json
from tkinter import Tk, filedialog
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

walls = []
agent = Agent(400, 300, 0, walls)

def load_walls():
    global walls
    global agent
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filename:
        with open(filename, 'r') as f:
            walls = [Wall.from_dict(data) for data in json.load(f)]
    root.destroy()
    agent.walls = walls

def toggle_laser():
    global agent
    agent.lidar_visible = not agent.lidar_visible

buttons = [
    Button(850, 50, 100, 50, 'Load Walls', load_walls),
    Button(850, 110, 100, 50, "See LiDAR", toggle_laser),
]



# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.is_clicked(event.pos):
                    button.action()
        

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

    # Draw the walls
    for wall in walls:
        wall.draw(screen)

    for button in buttons:
        button.draw(screen)

    # Update the display
    pygame.display.flip()


    print(agent.lidar_ranges)

# Quit pygame
pygame.quit()
sys.exit()