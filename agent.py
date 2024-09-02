import math
import pygame
from colors import RED

# Define the boundaries of the robot area
LEFT_BOUNDARY = 0
RIGHT_BOUNDARY = 800
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 600


class Agent:
    def __init__(self, x, y, direction, walls, num_lidar_beams=720):
        self.x = x
        self.y = y
        self.direction = direction  # in degrees
        self.linear_speed = 10
        self.body_radius = 20
        self.angular_speed = 5
        self.lidar_max_range = 2000
        self.lidar_angles = [
            i * (360 / num_lidar_beams) for i in range(num_lidar_beams)
        ]
        self.lidar_ranges = []
        self.lidar_visible = False
        self.bump_sensor = False
        self.walls = walls

    def draw(self, screen):
        # Calculate the end point of the arrow
        end_x = self.x + self.body_radius * math.cos(math.radians(self.direction))
        end_y = self.y - self.body_radius * math.sin(math.radians(self.direction))

        # Draw the LiDAR beams if visible
        if self.lidar_visible:
            self.draw_lidar(screen)

        # Draw the circle
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), self.body_radius)

        # Draw the arrow
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)

    def draw_lidar(self, screen):
        for angle, distance in zip(self.lidar_angles, self.lidar_ranges):
            laser_angle = math.radians(self.direction + angle)
            end_x = self.x + distance * math.cos(laser_angle)
            end_y = self.y - distance * math.sin(laser_angle)
            pygame.draw.line(screen, (0, 255, 0), (self.x, self.y), (end_x, end_y), 1)
            # Debug visualization
            pygame.draw.circle(
                screen, RED, (int(end_x), int(end_y)), 3
            )  # Draw the laser endpoint

    def scan(self):
        self.lidar_ranges = []
        agent_x, agent_y = int(self.x), int(self.y)

        for angle in self.lidar_angles:
            laser_angle = math.radians(self.direction + angle)
            end_x = agent_x + self.lidar_max_range * math.cos(laser_angle)
            end_y = agent_y - self.lidar_max_range * math.sin(laser_angle)

            # Round the laser endpoints to reduce precision
            end_x, end_y = int(end_x), int(end_y)

            # Initialize the minimum distance with the max range
            min_distance = self.lidar_max_range

            # Check for collisions with walls first
            for wall in self.walls:
                collision_distance = wall.line_intersection(
                    agent_x, agent_y, end_x, end_y
                )
                if collision_distance is not None:
                    min_distance = min(min_distance, collision_distance)

            # Check for collisions with boundaries only if no wall collision is closer
            boundary_collision = self.check_lidar_collision_with_boundaries(
                agent_x, agent_y, end_x, end_y
            )
            if boundary_collision[2] < min_distance:
                min_distance = boundary_collision[2]

            # Append the closest distance to the lidar_ranges
            self.lidar_ranges.append(min_distance)

    def check_lidar_collision_with_boundaries(self, start_x, start_y, end_x, end_y):
        dx = end_x - start_x
        dy = end_y - start_y

        # Check collision with all four boundaries
        collisions = []

        # Top boundary
        if dy < 0:
            t = (TOP_BOUNDARY - start_y) / dy if dy != 0 else float("inf")
            if 0 <= t <= 1:
                collisions.append((start_x + t * dx, TOP_BOUNDARY, t))

        # Bottom boundary
        if dy > 0:
            t = (BOTTOM_BOUNDARY - start_y) / dy if dy != 0 else float("inf")
            if 0 <= t <= 1:
                collisions.append((start_x + t * dx, BOTTOM_BOUNDARY, t))

        # Left boundary
        if dx < 0:
            t = (LEFT_BOUNDARY - start_x) / dx if dx != 0 else float("inf")
            if 0 <= t <= 1:
                collisions.append((LEFT_BOUNDARY, start_y + t * dy, t))

        # Right boundary
        if dx > 0:
            t = (RIGHT_BOUNDARY - start_x) / dx if dx != 0 else float("inf")
            if 0 <= t <= 1:
                collisions.append((RIGHT_BOUNDARY, start_y + t * dy, t))

        if collisions:
            # Sort collisions by distance (represented by t)
            collisions.sort(key=lambda c: c[2])
            collision_x, collision_y, t = collisions[0]
            boundary_distance = math.sqrt(
                (collision_x - start_x) ** 2 + (collision_y - start_y) ** 2
            )
            return collision_x, collision_y, boundary_distance

        return end_x, end_y, self.lidar_max_range

    def detect_collision(self, move_forward=True):
        # Calculate the next position
        if move_forward:
            next_x = self.x + self.linear_speed * math.cos(math.radians(self.direction))
            next_y = self.y - self.linear_speed * math.sin(math.radians(self.direction))
        else:
            next_x = self.x - self.linear_speed * math.cos(math.radians(self.direction))
            next_y = self.y + self.linear_speed * math.sin(math.radians(self.direction))

        # Check if the next position is within the boundaries considering the radius of the agent
        if not (
            LEFT_BOUNDARY + self.body_radius
            <= next_x
            <= RIGHT_BOUNDARY - self.body_radius
            and TOP_BOUNDARY + self.body_radius
            <= next_y
            <= BOTTOM_BOUNDARY - self.body_radius
        ):
            return True

        # Check for collision with walls
        for wall in self.walls:
            if wall.is_colliding(next_x, next_y, self.body_radius):
                return True

        return False

    def try_move(self, move_forward=True):
        original_speed = self.linear_speed
        while self.linear_speed > 0:
            if not self.detect_collision(move_forward):
                if move_forward:
                    self.x += self.linear_speed * math.cos(math.radians(self.direction))
                    self.y -= self.linear_speed * math.sin(math.radians(self.direction))
                else:
                    self.x -= self.linear_speed * math.cos(math.radians(self.direction))
                    self.y += self.linear_speed * math.sin(math.radians(self.direction))
                self.bump_sensor = False
                break
            self.linear_speed -= 0.1
        self.linear_speed = original_speed
        if self.linear_speed <= 0:
            self.bump_sensor = True

    def move_forward(self):
        if not self.detect_collision(move_forward=True):
            self.x += self.linear_speed * math.cos(math.radians(self.direction))
            self.y -= self.linear_speed * math.sin(math.radians(self.direction))
            self.bump_sensor = False
        else:
            self.bump_sensor = True

    def move_backward(self):
        if not self.detect_collision(move_forward=False):
            self.x -= self.linear_speed * math.cos(math.radians(self.direction))
            self.y += self.linear_speed * math.sin(math.radians(self.direction))
            self.bump_sensor = False
        else:
            self.bump_sensor = True

    def rotate_left(self):
        self.direction = (self.direction + self.angular_speed) % 360
        self.bump_sensor = False

    def rotate_right(self):
        self.direction = (self.direction - self.angular_speed) % 360
        self.bump_sensor = False

    def handle_move_keys(self, keys):
        if keys[pygame.K_LEFT]:
            self.rotate_left()
        if keys[pygame.K_RIGHT]:
            self.rotate_right()
        if keys[pygame.K_UP]:
            self.try_move(move_forward=True)
        if keys[pygame.K_DOWN]:
            self.try_move(move_forward=False)
