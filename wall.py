import pygame
import math
from colors import *


class Wall:
    HANDLE_SIZE = 5  # Reasonably sized handles

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.selected = False
        self.resizing = False
        self.resize_dir = None

    def is_point_within_wall(self, x, y):
        return self.rect.collidepoint(x, y)

    def is_colliding(self, x, y, radius):
        # Check if the point (x, y) with the given radius is colliding with the wall
        closest_x = max(self.rect.left, min(x, self.rect.right))
        closest_y = max(self.rect.top, min(y, self.rect.bottom))
        distance_x = x - closest_x
        distance_y = y - closest_y
        return (distance_x**2 + distance_y**2) < (radius**2)

    def line_intersection(self, x1, y1, x2, y2):
        # Calculate the intersection point of a line (x1, y1) -> (x2, y2) with the wall's rectangle
        rect_lines = [
            ((self.rect.left, self.rect.top), (self.rect.right, self.rect.top)),  # Top
            (
                (self.rect.right, self.rect.top),
                (self.rect.right, self.rect.bottom),
            ),  # Right
            (
                (self.rect.right, self.rect.bottom),
                (self.rect.left, self.rect.bottom),
            ),  # Bottom
            (
                (self.rect.left, self.rect.bottom),
                (self.rect.left, self.rect.top),
            ),  # Left
        ]

        def line_intersection_helper(line1, line2):
            (x1, y1), (x2, y2) = line1
            (x3, y3), (x4, y4) = line2

            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

            if abs(denom) < 1e-10:  # Handle near-parallel lines
                return None

            px = (
                (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
            ) / denom
            py = (
                (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
            ) / denom

            if (
                min(x1, x2) <= px <= max(x1, x2)
                and min(y1, y2) <= py <= max(y1, y2)
                and min(x3, x4) <= px <= max(x3, x4)
                and min(y3, y4) <= py <= max(y3, y4)
            ):
                return px, py

            return None

        # Initialize the minimum distance to None or a large value
        min_distance = None

        lidar_line = ((x1, y1), (x2, y2))
        for rect_line in rect_lines:
            collision_point = line_intersection_helper(lidar_line, rect_line)
            if collision_point:
                intersection_x, intersection_y = collision_point
                distance = math.sqrt(
                    (intersection_x - x1) ** 2 + (intersection_y - y1) ** 2
                )

                # Update min_distance if this intersection is closer
                if min_distance is None or distance < min_distance:
                    min_distance = distance

        return min_distance

    def draw(self, screen):
        pygame.draw.rect(screen, BROWN, self.rect)  # Fill the wall with brown
        edge_color = BLUE if self.selected else BLACK
        pygame.draw.rect(screen, edge_color, self.rect, 2)  # Draw edges
        if self.selected:
            self.draw_handles(screen)

    def draw_handles(self, screen):
        handles = self.get_handles()
        for handle in handles:
            pygame.draw.rect(screen, GREEN, handle)

    def get_handles(self):
        x, y, w, h = self.rect
        hs = self.HANDLE_SIZE
        return [
            pygame.Rect(x, y, hs, hs),  # Top-left
            pygame.Rect(x + w - hs, y, hs, hs),  # Top-right
            pygame.Rect(x, y + h - hs, hs, hs),  # Bottom-left
            pygame.Rect(x + w - hs, y + h - hs, hs, hs),  # Bottom-right
            pygame.Rect(x + w // 2 - hs // 2, y, hs, hs),  # Top-center
            pygame.Rect(x + w // 2 - hs // 2, y + h - hs, hs, hs),  # Bottom-center
            pygame.Rect(x, y + h // 2 - hs // 2, hs, hs),  # Left-center
            pygame.Rect(x + w - hs, y + h // 2 - hs // 2, hs, hs),  # Right-center
        ]

    def handle_resize(self, mouse_pos):
        if not self.resizing:
            return
        x, y = mouse_pos
        if self.resize_dir == "top-left":
            self.rect.width += self.rect.x - x
            self.rect.height += self.rect.y - y
            self.rect.x = x
            self.rect.y = y
        elif self.resize_dir == "top-right":
            self.rect.width = x - self.rect.x
            self.rect.height += self.rect.y - y
            self.rect.y = y
        elif self.resize_dir == "bottom-left":
            self.rect.width += self.rect.x - x
            self.rect.x = x
            self.rect.height = y - self.rect.y
        elif self.resize_dir == "bottom-right":
            self.rect.width = x - self.rect.x
            self.rect.height = y - self.rect.y
        elif self.resize_dir == "top-center":
            self.rect.height += self.rect.y - y
            self.rect.y = y
        elif self.resize_dir == "bottom-center":
            self.rect.height = y - self.rect.y
        elif self.resize_dir == "left-center":
            self.rect.width += self.rect.x - x
            self.rect.x = x
        elif self.resize_dir == "right-center":
            self.rect.width = x - self.rect.x

    def to_dict(self):
        return {
            "x": self.rect.x,
            "y": self.rect.y,
            "width": self.rect.width,
            "height": self.rect.height,
        }

    @staticmethod
    def from_dict(data):
        return Wall(data["x"], data["y"], data["width"], data["height"])
