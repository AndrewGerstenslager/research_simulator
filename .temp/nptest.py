import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

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

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    checkbox1_rect = pygame.Rect(50, 50, 20, 20)
    checkbox2_rect = pygame.Rect(50, 100, 20, 20)
    selected_checkbox = None

    # Initialize Matplotlib
    fig, ax_radial = plt.subplots(subplot_kw={'projection': 'polar'})
    canvas_radial = FigureCanvas(fig)

    fig2, ax_scatter = plt.subplots()
    canvas_scatter = FigureCanvas(fig2)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if checkbox1_rect.collidepoint(event.pos):
                    if selected_checkbox == 'checkbox1':
                        selected_checkbox = None
                    else:
                        selected_checkbox = 'checkbox1'
                elif checkbox2_rect.collidepoint(event.pos):
                    if selected_checkbox == 'checkbox2':
                        selected_checkbox = None
                    else:
                        selected_checkbox = 'checkbox2'

        screen.fill((255, 255, 255))

        # Draw the checkboxes
        pygame.draw.rect(screen, (0, 0, 0), checkbox1_rect, 2)
        if selected_checkbox == 'checkbox1':
            pygame.draw.line(screen, (0, 0, 0), (checkbox1_rect.left, checkbox1_rect.top), (checkbox1_rect.right, checkbox1_rect.bottom), 2)
            pygame.draw.line(screen, (0, 0, 0), (checkbox1_rect.right, checkbox1_rect.top), (checkbox1_rect.left, checkbox1_rect.bottom), 2)

        pygame.draw.rect(screen, (0, 0, 0), checkbox2_rect, 2)
        if selected_checkbox == 'checkbox2':
            pygame.draw.line(screen, (0, 0, 0), (checkbox2_rect.left, checkbox2_rect.top), (checkbox2_rect.right, checkbox2_rect.bottom), 2)
            pygame.draw.line(screen, (0, 0, 0), (checkbox2_rect.right, checkbox2_rect.top), (checkbox2_rect.left, checkbox2_rect.bottom), 2)

        if selected_checkbox == 'checkbox1':
            # Sample data (replace this with your actual LiDAR data)
            distances = np.random.uniform(0.5, 10, 360)
            # Update radial plot with new data
            update_radial_plot(ax_radial, canvas_radial, distances)
            # Convert Matplotlib plot to Pygame surface
            plot_surface = plot_to_surface(canvas_radial)
            # Draw the plot surface on the Pygame screen
            screen.blit(plot_surface, (150, 50))  # Adjust position as needed
        elif selected_checkbox == 'checkbox2':
            # Update scatter plot with new data
            update_scatter_plot(ax_scatter, canvas_scatter)
            # Convert Matplotlib plot to Pygame surface
            plot_surface = plot_to_surface(canvas_scatter)
            # Draw the plot surface on the Pygame screen
            screen.blit(plot_surface, (150, 50))  # Adjust position as needed

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
