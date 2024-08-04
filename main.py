import pygame
import sys
import json
from tkinter import Tk, filedialog
from agent import Agent
from wall import Wall
from button import Button
from colors import *
from basic_controller import BasicController

def load_walls_file_dialogue():
    '''
    Uses the tkinter file dialogue to select the file to open. 
    Calls open_walls after file selected.
    '''
    global root
    root = Tk()
    root.withdraw()
    load_walls(filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")]))

def load_walls(filename):
    '''
    Takes the file name and loads in the file.
    Puts all wall objects into the wall object and updates agent's internal memory.
    '''
    global agent
    global walls
    if filename:
        with open(filename, 'r') as f:
            walls = [Wall.from_dict(data) for data in json.load(f)]
        walls = walls 
        agent.walls = walls

def toggle_laser():
    '''Thin wrapper to update whether to render LiDAR laser beams.'''
    global agent
    agent.lidar_visible = not agent.lidar_visible

def toggle_controller_running():
    '''Thin wrapper to update whether the controller is running or not.'''
    global controller, text_surfaces
    controller.running = not controller.running
    text_surfaces[4] = font.render("Controller ENABLED" if controller.running else "Controller DISABLED", True, GREEN if controller.running else RED)

# Initialize pygame
pygame.init()

# Define the clock for pygame
clock = pygame.time.Clock()

# Set up the display window
screen = pygame.display.set_mode((1600, 600))
pygame.display.set_caption('Simulation Window')

# Define the boundaries of the robot area
LEFT_BOUNDARY = 0
RIGHT_BOUNDARY = 800
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 600

# Define core components of sim
walls = []
agent = Agent(400, 300, 0, walls)
controller = BasicController(model = None, agent = agent)

# Load in walls
load_walls('test.json')

# Define buttons
buttons = [
    Button(850, 50, 100, 50, 'Load Walls', load_walls_file_dialogue),
    Button(850, 110, 100, 50, "See LiDAR", toggle_laser),
    Button(850, 170, 100, 50, "Toggle Controller", toggle_controller_running)
]

# Define on-screen text that renders in a block
font = pygame.font.Font(None, 24)
text_surfaces = [
        font.render('Load Wall Shortcut: u', True, BLACK),
        font.render('See LiDAR Shortcut: i', True, BLACK),
        font.render('Quit sim shortcut: q', True, BLACK),
        font.render('Toggle Controller: c', True, BLACK),
        font.render("Controller ENABLED" if controller.running else "Controller DISABLED", True, GREEN if controller.running else RED),
        font.render('Move agent manually: Arrow Keys', True, BLACK),
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
            if event.key == pygame.K_u:
                buttons[0].action()
            if event.key == pygame.K_i:
                buttons[1].action()
            if event.key == pygame.K_c:
                buttons[2].action()
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
    
    # Agent scans environment
    agent.scan()
    
    # Controller does its work
    controller.handle_input()
    controller.move_agent()

    # Draw the agent
    agent.draw(screen)

    # Draw the walls
    for wall in walls:
        wall.draw(screen)
    
    # Draw the buttons
    for button in buttons:
        button.draw(screen)
    
    # Draw text
    x,y = 850,450  
    for surface in text_surfaces:
        screen.blit(surface, (x,y))
        y += 20
    
    # Update the display
    pygame.display.flip()

    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
