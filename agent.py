import math
import pygame

# Define the radius of the agent
AGENT_RADIUS = 20

# Define the boundaries of the robot area
LEFT_BOUNDARY = 0
RIGHT_BOUNDARY = 800
TOP_BOUNDARY = 0
BOTTOM_BOUNDARY = 600

class Agent:
    def __init__(self, x, y, direction, walls, num_lidar_beams=36):
        self.x = x
        self.y = y
        self.direction = direction  # in degrees
        self.linear_speed = 10
        self.angular_speed = 5
        self.lidar_max_range = 200
        self.lidar_angles = [i * (360 / num_lidar_beams) for i in range(num_lidar_beams)]
        self.lidar_ranges = []
        self.lidar_visible = False
        self.bump_sensor = False
        self.walls = walls

    def draw(self, screen):
        # Calculate the end point of the arrow
        end_x = self.x + AGENT_RADIUS * math.cos(math.radians(self.direction))
        end_y = self.y - AGENT_RADIUS * math.sin(math.radians(self.direction))
         
        # Draw the LiDAR beams if visible
        if self.lidar_visible:
            self.draw_lidar(screen)

        # Draw the circle
        pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y), AGENT_RADIUS)

        # Draw the arrow
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)

    def draw_lidar(self, screen):
        for angle, distance in zip(self.lidar_angles, self.lidar_ranges):
            laser_angle = math.radians(self.direction + angle)
            end_x = self.x + distance * math.cos(laser_angle)
            end_y = self.y - distance * math.sin(laser_angle)
            pygame.draw.line(screen, (0, 255, 0), (self.x, self.y), (end_x, end_y), 1)

    def scan(self):
        self.lidar_ranges = []
        for angle in self.lidar_angles:
            laser_angle = math.radians(self.direction + angle)
            end_x = self.x + self.lidar_max_range * math.cos(laser_angle)
            end_y = self.y - self.lidar_max_range * math.sin(laser_angle)
            
            # Check for collisions with boundaries
            end_x, end_y, boundary_distance = self.check_collision_with_boundaries(end_x, end_y)
            
            # Check for collisions with walls
            wall_distance = self.lidar_max_range
            for wall in self.walls:
                collision_point = wall.get_collision_point(self.x, self.y, end_x, end_y)
                if collision_point:
                    end_x, end_y = collision_point
                    wall_distance = math.sqrt((end_x - self.x) ** 2 + (end_y - self.y) ** 2)
                    break
            
            # Calculate the distance to the collision point
            distance = min(boundary_distance, wall_distance)
            self.lidar_ranges.append(distance)

    def check_collision_with_boundaries(self, end_x, end_y):
        dx = end_x - self.x
        dy = end_y - self.y
        
        # Check collision with all four boundaries
        collisions = []
        
        # Top boundary
        if dy < 0:
            t = (TOP_BOUNDARY - self.y) / dy if dy != 0 else float('inf')
            if 0 <= t <= 1:
                collisions.append((self.x + t * dx, TOP_BOUNDARY, t))
        
        # Bottom boundary
        if dy > 0:
            t = (BOTTOM_BOUNDARY - self.y) / dy if dy != 0 else float('inf')
            if 0 <= t <= 1:
                collisions.append((self.x + t * dx, BOTTOM_BOUNDARY, t))
        
        # Left boundary
        if dx < 0:
            t = (LEFT_BOUNDARY - self.x) / dx if dx != 0 else float('inf')
            if 0 <= t <= 1:
                collisions.append((LEFT_BOUNDARY, self.y + t * dy, t))
        
        # Right boundary
        if dx > 0:
            t = (RIGHT_BOUNDARY - self.x) / dx if dx != 0 else float('inf')
            if 0 <= t <= 1:
                collisions.append((RIGHT_BOUNDARY, self.y + t * dy, t))
        
        if collisions:
            # Sort collisions by distance (represented by t)
            collisions.sort(key=lambda c: c[2])
            collision_x, collision_y, t = collisions[0]
            boundary_distance = math.sqrt((collision_x - self.x)**2 + (collision_y - self.y)**2)
            return collision_x, collision_y, boundary_distance
        
        return end_x, end_y, float('inf')

    def detect_collision(self, move_forward=True):
        # Calculate the next position
        if move_forward:
            next_x = self.x + self.linear_speed * math.cos(math.radians(self.direction))
            next_y = self.y - self.linear_speed * math.sin(math.radians(self.direction))
        else:
            next_x = self.x - self.linear_speed * math.cos(math.radians(self.direction))
            next_y = self.y + self.linear_speed * math.sin(math.radians(self.direction))

        # Check if the next position is within the boundaries considering the radius of the agent
        if not (LEFT_BOUNDARY + AGENT_RADIUS <= next_x <= RIGHT_BOUNDARY - AGENT_RADIUS and
                TOP_BOUNDARY + AGENT_RADIUS <= next_y <= BOTTOM_BOUNDARY - AGENT_RADIUS):
            return True

        # Check for collision with walls
        for wall in self.walls:
            if wall.is_colliding(next_x, next_y, AGENT_RADIUS):
                return True

        return False

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
            self.move_forward()
        if keys[pygame.K_DOWN]:
            self.move_backward()
