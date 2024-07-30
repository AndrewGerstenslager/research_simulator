# agent.py

import math
import pygame

class Agent:
    def __init__(self, x, y, orientation=0, num_lasers=360, num_visible_lasers=360):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.speed = 0
        self.radius = 20
        self.color = (255, 0, 0)
        self.arrow_length = 20
        self.num_lasers = num_lasers
        self.num_visible_lasers = num_visible_lasers
        self.max_lidar_range = 200
        self.lidar_data = []

    def move(self, keys):
        if keys[pygame.K_UP] and keys[pygame.K_DOWN]:
            self.speed = 0
        elif keys[pygame.K_UP]:
            self.speed = 2
        elif keys[pygame.K_DOWN]:
            self.speed = -2
        else:
            self.speed = 0

        if keys[pygame.K_LEFT]:
            self.orientation -= 0.1
        elif keys[pygame.K_RIGHT]:
            self.orientation += 0.1

        self.x += math.cos(self.orientation) * self.speed
        self.y += math.sin(self.orientation) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        arrow_x = int(self.x + math.cos(self.orientation) * self.arrow_length)
        arrow_y = int(self.y + math.sin(self.orientation) * self.arrow_length)
        pygame.draw.line(screen, (0, 0, 0), (int(self.x), int(self.y)), (arrow_x, arrow_y), 5)

    def get_position(self):
        return self.x, self.y

    def get_orientation(self):
        return self.orientation

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def get_laser_angles(self):
        step = self.num_lasers // self.num_visible_lasers
        return [i * 2 * math.pi / self.num_lasers for i in range(0, self.num_lasers, step)]

    def cast_lidar_beam(self, environment, max_range):
        laser_angles = self.get_laser_angles()
        beams = []
        for angle in laser_angles:
            laser_angle = self.orientation + angle
            end_x = self.x + math.cos(laser_angle) * max_range
            end_y = self.y + math.sin(laser_angle) * max_range

            for wall in environment.walls:
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
                        (self.x, self.y), (end_x, end_y), p1, p2)
                    if intersect:
                        end_x, end_y = intersect

            beams.append((end_x, end_y))
        return beams

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

