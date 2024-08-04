# obstacle.py

import pygame
from pygame.math import Vector2

class Obstacle:
    def __init__(self, location):
        self.location = Vector2(location)
        self.geometry = None  # To be defined in subclasses

    def is_point_within(self, point):
        raise NotImplementedError("This method should be overridden by subclasses")

class Wall(Obstacle):
    def __init__(self, location, width, height):
        super().__init__(location)
        self.width = width
        self.height = height
        self.geometry = pygame.Rect(location[0], location[1], width, height)

    def is_point_within(self, point):
        return self.geometry.collidepoint(point)

def check_laser_collisions(laser_origin, laser_direction, obstacles):
    """
    Check for collisions between a laser and a list of obstacles.
    
    :param laser_origin: The starting point of the laser (Vector2).
    :param laser_direction: The direction vector of the laser (Vector2).
    :param obstacles: List of Obstacle objects.
    :return: List of collision points.
    """
    collision_points = []
    for obstacle in obstacles:
        if isinstance(obstacle, Wall):
            # Check for intersection with the wall's geometry
            collision_point = laser_intersects_rect(laser_origin, laser_direction, obstacle.geometry)
            if collision_point:
                collision_points.append(collision_point)
    return collision_points

def laser_intersects_rect(origin, direction, rect):
    """
    Check if a laser intersects with a rectangle.
    
    :param origin: The starting point of the laser (Vector2).
    :param direction: The direction vector of the laser (Vector2).
    :param rect: The rectangle to check against (pygame.Rect).
    :return: The point of intersection or None.
    """
    # Implement ray-rectangle intersection logic
    # This is a placeholder for the actual intersection logic
    return None

# Example usage
if __name__ == "__main__":
    wall = Wall((100, 100), 50, 10)
    laser_origin = Vector2(0, 0)
    laser_direction = Vector2(1, 1).normalize()
    obstacles = [wall]
    collisions = check_laser_collisions(laser_origin, laser_direction, obstacles)
    print(collisions)