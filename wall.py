import pygame
import math
from constants import *


class Wall:
    HANDLE_SIZE = 5  # Reasonably sized handles

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.selected = False
        self.resizing = False
        self.resize_dir = None
        self.edges = [
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

    def is_colliding(self, x, y, radius):
        # Check if the point (x, y) with the given radius is colliding with the wall
        closest_x = max(self.rect.left, min(x, self.rect.right))
        closest_y = max(self.rect.top, min(y, self.rect.bottom))
        distance_x = x - closest_x
        distance_y = y - closest_y
        return (distance_x**2 + distance_y**2) < (radius**2)

    def line_intersection(self, x1, y1, x2, y2):
        def line_intersection_helper(line1, line2):
            (x1, y1), (x2, y2) = line1
            (x3, y3), (x4, y4) = line2

            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

            if abs(denom) < 1e-10:  # Handle near-parallel lines
                return None

            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

            if 0 <= t <= 1 and 0 <= u <= 1:
                return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

            return None

        lidar_line = ((x1, y1), (x2, y2))
        min_distance = float("inf")

        for rect_line in self.edges:
            collision_point = line_intersection_helper(lidar_line, rect_line)
            if collision_point:
                distance = math.hypot(collision_point[0] - x1, collision_point[1] - y1)
                if distance < min_distance:
                    min_distance = distance

        return min_distance if min_distance != float("inf") else None

    def draw(self, screen, draw_center=False):
        pygame.draw.rect(screen, BROWN, self.rect)  # Fill the wall with brown
        edge_color = BLUE if self.selected else BLACK
        pygame.draw.rect(screen, edge_color, self.rect, 2)  # Draw edges
        if self.selected:
            self.draw_handles(screen)

        # Draw X in center if specified
        if draw_center:
            center_x = self.rect.x + self.rect.width // 2
            center_y = self.rect.y + self.rect.height // 2
            size = 5
            pygame.draw.line(
                screen,
                BLACK,
                (center_x - size, center_y - size),
                (center_x + size, center_y + size),
            )
            pygame.draw.line(
                screen,
                BLACK,
                (center_x - size, center_y + size),
                (center_x + size, center_y - size),
            )

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

        # Store original rect for reverting if needed
        original_rect = self.rect.copy()

        # Minimum size for walls
        MIN_SIZE = 10

        # Handle different resize directions
        if self.resize_dir == "top-left":
            new_width = self.rect.right - x
            new_height = self.rect.bottom - y
            if new_width >= MIN_SIZE and new_height >= MIN_SIZE:
                self.rect.x = x
                self.rect.y = y
                self.rect.width = new_width
                self.rect.height = new_height
        elif self.resize_dir == "top-right":
            new_width = x - self.rect.x
            new_height = self.rect.bottom - y
            if new_width >= MIN_SIZE and new_height >= MIN_SIZE:
                self.rect.y = y
                self.rect.width = new_width
                self.rect.height = new_height
        elif self.resize_dir == "bottom-left":
            new_width = self.rect.right - x
            new_height = y - self.rect.y
            if new_width >= MIN_SIZE and new_height >= MIN_SIZE:
                self.rect.x = x
                self.rect.width = new_width
                self.rect.height = new_height
        elif self.resize_dir == "bottom-right":
            new_width = x - self.rect.x
            new_height = y - self.rect.y
            if new_width >= MIN_SIZE and new_height >= MIN_SIZE:
                self.rect.width = new_width
                self.rect.height = new_height
        elif self.resize_dir == "top-center":
            new_height = self.rect.bottom - y
            if new_height >= MIN_SIZE:
                self.rect.y = y
                self.rect.height = new_height
        elif self.resize_dir == "bottom-center":
            new_height = y - self.rect.y
            if new_height >= MIN_SIZE:
                self.rect.height = new_height
        elif self.resize_dir == "left-center":
            new_width = self.rect.right - x
            if new_width >= MIN_SIZE:
                self.rect.x = x
                self.rect.width = new_width
        elif self.resize_dir == "right-center":
            new_width = x - self.rect.x
            if new_width >= MIN_SIZE:
                self.rect.width = new_width

        # Check if the new position/size is within boundaries
        if (
            self.rect.left < 0
            or self.rect.right > 800  # Assuming RIGHT_BOUNDARY is 800
            or self.rect.top < 0
            or self.rect.bottom > 600
        ):  # Assuming BOTTOM_BOUNDARY is 600
            # Revert changes if outside boundaries
            self.rect = original_rect

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
