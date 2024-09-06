import io
import pygame
import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tkinter import Tk, filedialog
from agent import Agent
from wall import Wall
from button import Button
from constants import (
    LEFT_BOUNDARY,
    RIGHT_BOUNDARY,
    TOP_BOUNDARY,
    BOTTOM_BOUNDARY,
    GREEN,
    RED,
    BLACK,
)
from controller_random import RandomController
from text_input import TextInput

from AlabiHippocampalModel.layers.head_direction_layer import HeadDirectionLayer
from AlabiHippocampalModel.layers.boundary_vector_cell_layer import (
    BoundaryVectorCellLayer,
)


# General function to convert any Matplotlib plot to a Pygame surface
def plot_to_surface(fig):
    """Converts a Matplotlib figure to a Pygame surface."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png")  # Save plot to buffer as a PNG
    plt.close(fig)  # Close the plot
    buf.seek(0)
    img = Image.open(buf)
    img = img.resize((400, 300))  # Resize to fit the Pygame window space
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


def load_walls_file_dialogue():
    """
    Uses the tkinter file dialogue to select the file to open.
    Calls open_walls after file selected.
    """
    global root
    root = Tk()
    root.withdraw()
    load_walls(
        filedialog.askopenfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
    )


def load_walls(filename):
    """
    Takes the file name and loads in the file.
    Puts all wall objects into the wall object and updates agent's internal memory.
    """
    global agent
    global walls
    if filename:
        with open(filename, "r") as f:
            walls = [Wall.from_dict(data) for data in json.load(f)]
        walls = walls
        agent.walls = walls


def toggle_laser():
    """Thin wrapper to update whether to render LiDAR laser beams."""
    global agent
    agent.lidar_visible = not agent.lidar_visible


def toggle_controller_running():
    """Thin wrapper to update whether the controller is running or not."""
    global controller, text_surfaces
    controller.running = not controller.running
    text_surfaces[4] = font.render(
        "Controller ENABLED" if controller.running else "Controller DISABLED",
        True,
        GREEN if controller.running else RED,
    )


def set_clock_rate():
    """Sets the clock rate to the value in the text input field."""
    global clock_rate, clock, text_surfaces
    try:
        clock_rate = int(clock_rate_input.get_text())
        text_surfaces[6] = font.render(f"Clock Rate: {clock_rate}", True, BLACK)
    except ValueError:
        pass


def set_max_speed():
    """Sets the clock rate to 0 (max speed) or back to the previous clock rate."""
    global clock_rate, clock, max_speed, text_surfaces, previous_clock_rate
    if max_speed:
        max_speed = False
        clock_rate = previous_clock_rate
        text_surfaces[6] = font.render(f"Clock Rate: {clock_rate}", True, BLACK)
    else:
        max_speed = True
        previous_clock_rate = clock_rate
        clock_rate = 0
        text_surfaces[6] = font.render("Clock Rate: MAX", True, BLACK)


# Initialize pygame
pygame.init()

# Define the clock for pygame
clock = pygame.time.Clock()

# Set up the display window
screen = pygame.display.set_mode((1600, 600))
pygame.display.set_caption("Simulation Window")

# Define core components of sim
walls = []
agent = Agent(x=400, y=300, direction=0, walls=walls)
controller = RandomController(model=None, agent=agent)

# Load in walls
load_walls("worlds/test3.json")

# Define clock rate variable
clock_rate = 60
previous_clock_rate = clock_rate
max_speed = False

hd_layer = HeadDirectionLayer(num_cells=8, theta_0=0.0, unit="degree")
bvc_layer = BoundaryVectorCellLayer(
    max_dist=300,
    input_dim=360,
    n_hd=8,
    sigma_ang=90,
    sigma_d=20,
)

# Define buttons
buttons = [
    Button(850, 50, 100, 50, "Load Walls", load_walls_file_dialogue),
    Button(850, 110, 100, 50, "See LiDAR", toggle_laser),
    Button(850, 170, 100, 50, "Toggle Controller", toggle_controller_running),
    Button(850, 230, 100, 50, "Set Clock Rate", set_clock_rate),
    Button(850, 290, 100, 50, "Max Speed", set_max_speed),
]


clock_rate_input = TextInput(x=960, y=230, width=50, height=50)

# Define on-screen text that renders in a block
font = pygame.font.Font(None, 24)
text_surfaces = [
    font.render("Load Wall Shortcut: u", True, BLACK),
    font.render("See LiDAR Shortcut: i", True, BLACK),
    font.render("Quit sim shortcut: q", True, BLACK),
    font.render("Toggle Controller: c", True, BLACK),
    font.render(
        "Controller ENABLED" if controller.running else "Controller DISABLED",
        True,
        GREEN if controller.running else RED,
    ),
    font.render("Move agent manually: Arrow Keys", True, BLACK),
    font.render(f"Clock Rate: {clock_rate}", True, BLACK),
    font.render("Actual Speed: Calculating...", True, BLACK),
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
            if event.key == pygame.K_m:
                buttons[4].action()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.is_clicked(event.pos):
                    button.action()
        clock_rate_input.handle_event(event)

    # Get the state of all keyboard buttons
    keys = pygame.key.get_pressed()

    # Handle agent's movement
    agent.handle_move_keys(keys)

    # Fill the screen with a white color
    screen.fill((255, 255, 255))

    # Draw the left half as the navigation area
    pygame.draw.rect(
        screen,
        (200, 200, 200),
        (
            LEFT_BOUNDARY,
            TOP_BOUNDARY,
            RIGHT_BOUNDARY - LEFT_BOUNDARY,
            BOTTOM_BOUNDARY - TOP_BOUNDARY,
        ),
    )

    # Agent scans environment
    agent.scan()

    # Controller does its work
    controller.handle_input()
    controller.move_agent()

    # Draw the walls
    for wall in walls:
        wall.draw(screen)

    # Draw the agent
    agent.draw(screen)

    fig = bvc_layer.plot_activation(
        np.array(agent.lidar_ranges),
        np.deg2rad(np.array(agent.lidar_angles)),
        return_plot=True,
    )
    plot_surface = plot_to_surface(fig)
    screen.blit(plot_surface, (1200, 100))

    # Draw the buttons
    for button in buttons:
        button.draw(screen)

    # Draw text input
    clock_rate_input.update()
    clock_rate_input.draw(screen)

    # Draw text
    x, y = 1300, 400
    for surface in text_surfaces:
        screen.blit(surface, (x, y))
        y += 20

    # Update the display
    pygame.display.flip()

    # Control the frame rate and measure actual frame rate if at max speed
    if clock_rate > 0:
        clock.tick(clock_rate)
        actual_speed = clock_rate
    else:
        actual_speed = int(clock.get_fps())
        text_surfaces[7] = font.render(f"Actual Speed: {actual_speed} FPS", True, BLACK)
        clock.tick()

# Quit pygame
pygame.quit()
sys.exit()
