# environment.py

import pygame
import math

class Environment:
    def __init__(self, play_area_width, screen_height):
        self.play_area_width = play_area_width
        self.screen_height = screen_height
        self.walls = [
            pygame.Rect(200, 150, 20, 100),
            pygame.Rect(400, 250, 20, 100)
        ]
        self.checkbox_lidar_rect = pygame.Rect(play_area_width + 20, 20, 20, 20)
        self.checkbox_radial_graph_rect = pygame.Rect(play_area_width + 20, 60, 20, 20)
        self.checkbox_scatter_plot_rect = pygame.Rect(play_area_width + 20, 100, 20, 20)
        self.lidar_visible = True
        self.radial_graph_visible = False
        self.scatter_plot_visible = False

    def check_wall_collision(self, robot_rect):
        for wall in self.walls:
            if robot_rect.colliderect(wall):
                return True
        return False

    def check_play_area_collision(self, new_robot_x, new_robot_y, robot_radius):
        if new_robot_x - robot_radius < 0 or new_robot_x + robot_radius > self.play_area_width:
            return True
        if new_robot_y - robot_radius < 0 or new_robot_y + robot_radius > self.screen_height:
            return True
        return False

    def cast_lidar_beam(self, robot_x, robot_y, angle, max_range):
        end_x = robot_x + math.cos(angle) * max_range
        end_y = robot_y + math.sin(angle) * max_range

        for wall in self.walls:
            wall_rect = pygame.Rect(wall)
            wall_points = [
                (wall_rect.left, wall_rect.top),
                (wall_rect.left, wall_rect.bottom),
                (wall_rect.right, wall_rect.top),
                (wall_rect.right, wall_rect.bottom)
            ]
            for i in range(len(wall_points)):
                p1 = wall_points[i]
                p2 = wall_points[(i + 1) % len(wall_points)]
                intersect = self.line_intersection(
                    (robot_x, robot_y), (end_x, end_y), p1, p2)
                if intersect:
                    end_x, end_y = intersect

        return end_x, end_y

    def line_intersection(self, p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None

        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

        if (min(x1, x2) <= px <= max(x1, x2) and
            min(y1, y2) <= py <= max(y1, y2) and
            min(x3, x4) <= px <= max(x3, x4) and
            min(y3, y4) <= py <= max(y3, y4)):
            return px, py

        return None

    def toggle_lidar(self):
        self.lidar_visible = not self.lidar_visible

    def toggle_radial_graph(self):
        self.radial_graph_visible = not self.radial_graph_visible

    def toggle_scatter_plot(self):
        self.scatter_plot_visible = not self.scatter_plot_visible

    def draw(self, screen):
        # Draw the play area boundary
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, self.play_area_width, self.screen_height), 2)

        # Draw the walls
        for wall in self.walls:
            pygame.draw.rect(screen, (0, 0, 255), wall)

        # Draw the sidebar
        sidebar_width = screen.get_width() - self.play_area_width
        pygame.draw.rect(screen, (200, 200, 200), (self.play_area_width, 0, sidebar_width, self.screen_height))

        # Draw the checkboxes
        self.draw_checkbox(screen, self.checkbox_lidar_rect, self.lidar_visible, "LiDAR")
        self.draw_checkbox(screen, self.checkbox_radial_graph_rect, self.radial_graph_visible, "Radial Graph")
        self.draw_checkbox(screen, self.checkbox_scatter_plot_rect, self.scatter_plot_visible, "Scatter Plot")

    def draw_checkbox(self, screen, rect, checked, label):
        pygame.draw.rect(screen, (255, 255, 255), rect)
        if checked:
            pygame.draw.line(screen, (0, 0, 0), rect.topleft, rect.bottomright, 2)
            pygame.draw.line(screen, (0, 0, 0), rect.topright, rect.bottomleft, 2)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        font = pygame.font.SysFont(None, 24)
        text = font.render(label, True, (0, 0, 0))
        screen.blit(text, (rect.right + 10, rect.y))
