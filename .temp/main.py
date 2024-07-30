# main.py

import pygame
import sys
from agent import Agent
from environment import Environment
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Initialize the pygame library
pygame.init()

# Set up and initialize screen
screen_width, screen_height = 1100, 480  # Increased width to accommodate larger sidebar
play_area_width = 640  # Width of the play area
sidebar_width = screen_width - play_area_width
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Simple Robot Sim')

# Initialize Agent and Environment
robot_x, robot_y = play_area_width / 2, screen_height / 2
agent = Agent(robot_x, robot_y)
environment = Environment(play_area_width, screen_height)

# Initialize Matplotlib for plots
fig, ax_radial = plt.subplots(subplot_kw={'projection': 'polar'})
canvas_radial = FigureCanvas(fig)

fig2, ax_scatter = plt.subplots()
canvas_scatter = FigureCanvas(fig2)

def update_radial_plot(ax, canvas, distances):
    angles = np.linspace(0, 360, len(distances))
    angles_rad = np.deg2rad(angles)

    ax.clear()
    ax.plot(angles_rad, distances)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_title("LiDAR Output in Radial Plot")
    ax.set_xlabel("Angle (degrees)")
    ax.set_ylabel("Distance (meters)")

    canvas.draw()

def update_scatter_plot(ax, canvas):
    x = np.random.normal(0, 1, 100)
    y = np.random.normal(0, 1, 100)

    ax.clear()
    ax.scatter(x, y)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_title("Random Scatter Plot")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")

    canvas.draw()

def plot_to_surface(canvas):
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()

    return pygame.image.frombuffer(raw_data, size, "RGBA")

# Game Loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if environment.checkbox_lidar_rect.collidepoint(event.pos):
                environment.toggle_lidar()
            elif environment.checkbox_radial_graph_rect.collidepoint(event.pos):
                environment.toggle_radial_graph()
            elif environment.checkbox_scatter_plot_rect.collidepoint(event.pos):
                environment.toggle_scatter_plot()

    # Get key presses
    keys = pygame.key.get_pressed()

    # Move agent
    agent.move(keys)

    # Check for collisions
    robot_rect = agent.get_rect()
    if environment.check_wall_collision(robot_rect) or environment.check_play_area_collision(agent.x, agent.y, agent.radius):
        agent.speed = 0  # Stop the robot upon collision

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw environment and agent
    environment.draw(screen)
    

    # Draw the LiDAR rays
    if environment.lidar_visible:
        lidar_beams = agent.cast_lidar_beam(environment, agent.max_lidar_range)
        for end_x, end_y in lidar_beams:
            pygame.draw.line(screen, (0, 255, 0), (agent.x, agent.y), (end_x, end_y), 1)

    agent.draw(screen)

    # Draw the radial graph
    if environment.radial_graph_visible:
        # Sample data (replace this with your actual LiDAR data)
        distances = np.random.uniform(0.5, 10, 360)
        # Update radial plot with new data
        update_radial_plot(ax_radial, canvas_radial, distances)
        # Convert Matplotlib plot to Pygame surface
        plot_surface = plot_to_surface(canvas_radial)
        # Draw the plot surface on the Pygame screen
        screen.blit(plot_surface, (play_area_width + 20, 50))  # Adjust position as needed

    # Draw the scatter plot
    if environment.scatter_plot_visible:
        # Update scatter plot with new data
        update_scatter_plot(ax_scatter, canvas_scatter)
        # Convert Matplotlib plot to Pygame surface
        plot_surface = plot_to_surface(canvas_scatter)
        # Draw the plot surface on the Pygame screen
        screen.blit(plot_surface, (play_area_width + 20, 250))  # Adjust position as needed

    pygame.display.flip()
    pygame.time.Clock().tick(60)
