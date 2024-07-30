import pygame
from colors import *

class Wall:
    HANDLE_SIZE = 5  # Reasonably sized handles

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.selected = False
        self.resizing = False
        self.resize_dir = None

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
            pygame.Rect(x + w - hs, y + h // 2 - hs // 2, hs, hs)  # Right-center
        ]

    def handle_resize(self, mouse_pos):
        if not self.resizing:
            return
        x, y = mouse_pos
        if self.resize_dir == 'top-left':
            self.rect.width += self.rect.x - x
            self.rect.height += self.rect.y - y
            self.rect.x = x
            self.rect.y = y
        elif self.resize_dir == 'top-right':
            self.rect.width = x - self.rect.x
            self.rect.height += self.rect.y - y
            self.rect.y = y
        elif self.resize_dir == 'bottom-left':
            self.rect.width += self.rect.x - x
            self.rect.x = x
            self.rect.height = y - self.rect.y
        elif self.resize_dir == 'bottom-right':
            self.rect.width = x - self.rect.x
            self.rect.height = y - self.rect.y
        elif self.resize_dir == 'top-center':
            self.rect.height += self.rect.y - y
            self.rect.y = y
        elif self.resize_dir == 'bottom-center':
            self.rect.height = y - self.rect.y
        elif self.resize_dir == 'left-center':
            self.rect.width += self.rect.x - x
            self.rect.x = x
        elif self.resize_dir == 'right-center':
            self.rect.width = x - self.rect.x

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y, 'width': self.rect.width, 'height': self.rect.height}

    @staticmethod
    def from_dict(data):
        return Wall(data['x'], data['y'], data['width'], data['height'])

