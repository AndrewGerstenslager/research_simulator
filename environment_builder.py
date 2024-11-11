# %%
import pygame
import json
import math
import sys
from tkinter import Tk, filedialog
from wall import Wall
from button import Button
from constants import *
from text_input import TextInput
from agent import Agent

pygame.init()

# Initialize agent
agent = None
selected_agent = None

# Create text inputs for wall properties
text_inputs = {
    "x": TextInput(1000, 50, 150, 30, ""),
    "y": TextInput(1000, 120, 150, 30, ""),
    "width": TextInput(1000, 190, 150, 30, ""),
    "height": TextInput(1000, 260, 150, 30, ""),
}


def apply_wall_properties():
    global selected_wall, selected_agent
    if selected_wall:
        try:
            # Store original values
            original_rect = selected_wall.rect.copy()

            # Get new values
            center_x = int(text_inputs["x"].text)
            center_y = int(text_inputs["y"].text)
            width = int(text_inputs["width"].text)
            height = int(text_inputs["height"].text)

            # Convert center coordinates to top-left position
            x = center_x - width // 2
            y = center_y - height // 2

            # Apply new values
            selected_wall.rect.x = x
            selected_wall.rect.y = y
            selected_wall.rect.width = width
            selected_wall.rect.height = height

            # Check boundaries
            if (
                selected_wall.rect.left < LEFT_BOUNDARY
                or selected_wall.rect.right > RIGHT_BOUNDARY
                or selected_wall.rect.top < TOP_BOUNDARY
                or selected_wall.rect.bottom > BOTTOM_BOUNDARY
                or width < 10
                or height < 10
            ):  # Minimum size constraints
                # Revert if outside boundaries
                selected_wall.rect = original_rect
        except ValueError:
            pass  # Handle invalid input gracefully
    elif selected_agent:
        try:
            # Store original values
            original_x = selected_agent.x
            original_y = selected_agent.y
            original_radius = selected_agent.body_radius

            # Get new values
            x = int(text_inputs["x"].text)
            y = int(text_inputs["y"].text)
            radius = int(text_inputs["width"].text)  # Using width field for radius
            direction = int(
                text_inputs["height"].text
            )  # Using height field for rotation

            # Validate and apply new values
            if (
                LEFT_BOUNDARY + radius <= x <= RIGHT_BOUNDARY - radius
                and TOP_BOUNDARY + radius <= y <= BOTTOM_BOUNDARY - radius
                and radius >= 10
            ):  # Minimum radius constraint

                # Check for wall collisions
                can_move = True
                for wall in walls:
                    if wall.is_colliding(x, y, radius):
                        can_move = False
                        break

                if can_move:
                    selected_agent.x = x
                    selected_agent.y = y
                    selected_agent.body_radius = radius
                    selected_agent.direction = (
                        direction % 360
                    )  # Keep direction between 0-359

        except ValueError:
            pass  # Handle invalid input gracefully


# Screen setup
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Wall Editor")
selected_wall = None
copied_wall = None
is_dragging = False
walls = []


def save_environment():
    root = Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("JSON files", "*.json")]
    )
    if filename:
        world_data = {
            "walls": [{"wall": wall.to_dict()} for wall in walls],
            "agent": (
                {
                    "agent": {
                        "x": agent.x,
                        "y": agent.y,
                        "direction": agent.direction,
                        "radius": agent.body_radius,
                    }
                }
                if agent
                else None
            ),
        }
        with open(filename, "w") as f:
            json.dump(world_data, f)
    root.destroy()


def load_environment():
    global walls, agent
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        defaultextension=".json", filetypes=[("JSON files", "*.json")]
    )
    if filename:
        with open(filename, "r") as f:
            world_data = json.load(f)
            # Load walls
            walls = [
                Wall.from_dict(wall_data["wall"]) for wall_data in world_data["walls"]
            ]
            # Load agent if it exists
            if world_data["agent"]:
                agent_data = world_data["agent"]["agent"]
                agent = Agent(
                    agent_data["x"], agent_data["y"], agent_data["direction"], walls
                )
                agent.body_radius = agent_data["radius"]
            else:
                agent = None
    root.destroy()


def reset_world():
    global walls, agent, selected_agent
    walls = []
    agent = None
    selected_agent = None


def delete_agent():
    global agent, selected_agent
    agent = None
    selected_agent = None


def delete_selected_wall():
    global walls, selected_wall
    if selected_wall:
        walls.remove(selected_wall)
        selected_wall = None


def spawn_agent():
    global agent, selected_agent
    if agent is None:
        agent = Agent(400, 300, 0, walls)
        selected_agent = None  # Reset selected agent when spawning new one


def handle_mouse_events(event):
    # Handle text input events
    for text_input in text_inputs.values():
        text_input.handle_event(event)
    global selected_wall, copied_wall, is_dragging, selected_agent, agent
    if event.type == pygame.MOUSEBUTTONDOWN:
        is_dragging = False
        for button in buttons:
            if button.is_clicked(event.pos):
                button.action()
                return

        # Check for agent selection
        if agent:
            mouse_x, mouse_y = event.pos
            distance = math.sqrt((mouse_x - agent.x) ** 2 + (mouse_y - agent.y) ** 2)
            if distance <= agent.body_radius:
                selected_agent = agent
                selected_wall = None
                for wall in walls:
                    wall.selected = False
                return
            else:
                selected_agent = None
        for wall in walls:
            if wall.rect.collidepoint(event.pos):
                wall.selected = True
                selected_wall = wall
                for handle, direction in zip(
                    wall.get_handles(),
                    [
                        "top-left",
                        "top-right",
                        "bottom-left",
                        "bottom-right",
                        "top-center",
                        "bottom-center",
                        "left-center",
                        "right-center",
                    ],
                ):
                    if handle.collidepoint(event.pos):
                        wall.resizing = True
                        wall.resize_dir = direction
                        return
            else:
                wall.selected = False
                wall.resizing = False
                wall.resize_dir = None
    elif event.type == pygame.MOUSEBUTTONUP:
        if selected_wall:
            selected_wall.resizing = False
            selected_wall.resize_dir = None
        is_dragging = False
    elif event.type == pygame.MOUSEMOTION:
        if selected_wall and selected_wall.resizing:
            selected_wall.handle_resize(event.pos)
        elif selected_agent and event.buttons[0]:
            # Move agent with boundary checking
            new_x = event.pos[0]
            new_y = event.pos[1]

            # Ensure agent stays within boundaries
            new_x = max(
                LEFT_BOUNDARY + agent.body_radius,
                min(RIGHT_BOUNDARY - agent.body_radius, new_x),
            )
            new_y = max(
                TOP_BOUNDARY + agent.body_radius,
                min(BOTTOM_BOUNDARY - agent.body_radius, new_y),
            )

            # Check for wall collisions
            can_move = True
            for wall in walls:
                if wall.is_colliding(new_x, new_y, agent.body_radius):
                    can_move = False
                    break

            if can_move:
                agent.x = new_x
                agent.y = new_y

        elif (
            selected_wall and event.buttons[0]
        ):  # Check if the left mouse button is held down
            is_dragging = True
            # Store original position
            original_x = selected_wall.rect.x
            original_y = selected_wall.rect.y

            # Try to move
            selected_wall.rect.x += event.rel[0]
            selected_wall.rect.y += event.rel[1]

            # Check boundaries
            if (
                selected_wall.rect.left < LEFT_BOUNDARY
                or selected_wall.rect.right > RIGHT_BOUNDARY
                or selected_wall.rect.top < TOP_BOUNDARY
                or selected_wall.rect.bottom > BOTTOM_BOUNDARY
            ):
                # Revert if outside boundaries
                selected_wall.rect.x = original_x
                selected_wall.rect.y = original_y


def handle_keyboard_events(event):
    global selected_wall, copied_wall, is_dragging
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_c and selected_wall:
            copied_wall = Wall(
                selected_wall.rect.x,
                selected_wall.rect.y,
                selected_wall.rect.width,
                selected_wall.rect.height,
            )
        elif event.key == pygame.K_v and copied_wall:
            new_wall = Wall(0, 0, copied_wall.rect.width, copied_wall.rect.height)
            walls.append(new_wall)
        elif event.key == pygame.K_s:
            save_environment()
        elif event.key == pygame.K_l:
            load_environment()


def spawn_wall():
    new_wall = Wall(100, 100, 50, 50)
    walls.append(new_wall)


def paste_wall():
    if copied_wall:
        new_wall = Wall(0, 0, copied_wall.rect.width, copied_wall.rect.height)
        walls.append(new_wall)


def copy_wall():
    global copied_wall, selected_wall
    if selected_wall:
        copied_wall = Wall(
            selected_wall.rect.x,
            selected_wall.rect.y,
            selected_wall.rect.width,
            selected_wall.rect.height,
        )
        selected_wall.selected = False  # Deselect the wall after copying
        selected_wall = None


# Create buttons
buttons = [
    Button(1000, 330, 150, 50, "Apply Changes", apply_wall_properties),
    Button(850, 50, 120, 50, "Add Wall", spawn_wall),
    Button(850, 110, 120, 50, "Copy Wall", copy_wall),
    Button(
        850,
        170,
        120,
        50,
        "Paste Wall",
        paste_wall,
        color=DISABLED_GRAY if not copied_wall else BLACK,
    ),
    Button(850, 230, 120, 50, "Reset World", reset_world),
    Button(850, 290, 120, 50, "Delete Wall", delete_selected_wall),
    Button(850, 350, 120, 50, "Save World", save_environment),
    Button(850, 410, 120, 50, "Load World", load_environment),
    Button(850, 470, 120, 50, "Spawn Agent", spawn_agent),
    Button(850, 530, 120, 50, "Delete Agent", delete_agent),
]

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        handle_mouse_events(event)
        handle_keyboard_events(event)

    # Fill the screen with a white color
    screen.fill(WHITE)

    # Draw the left half as the navigation area
    pygame.draw.rect(
        screen,
        GRAY,
        (
            LEFT_BOUNDARY,
            TOP_BOUNDARY,
            RIGHT_BOUNDARY - LEFT_BOUNDARY,
            BOTTOM_BOUNDARY - TOP_BOUNDARY,
        ),
    )

    # Draw the walls
    for wall in walls:
        wall.draw(screen, draw_center=True)

    # Draw the agent if it exists
    if agent:
        agent.draw(screen)

    # Draw the buttons
    for button in buttons:
        if button.text == "Paste Wall":
            button.color = DISABLED_GRAY if not copied_wall else BLACK
        elif button.text == "Spawn Agent":
            button.color = DISABLED_GRAY if agent else BLACK
        elif button.text == "Delete Agent":
            button.color = DISABLED_GRAY if not agent else BLACK
        elif button.text == "Delete Wall":
            button.color = DISABLED_GRAY if not selected_wall else BLACK
        else:
            button.color = BLACK
        button.draw(screen)

    # Draw text input labels
    font = pygame.font.Font(None, 24)
    labels = ["Center X:", "Center Y:", "Width:", "Height:"]
    y_positions = [30, 100, 170, 240]

    for label, y_pos in zip(labels, y_positions):
        text_surface = font.render(label, True, BLACK)
        screen.blit(text_surface, (1000, y_pos))

    # Update text inputs with wall properties only when not active
    if selected_wall:
        for key, text_input in text_inputs.items():
            if not text_input.active:
                if key == "x":
                    text_input.text = str(selected_wall.rect.centerx)
                elif key == "y":
                    text_input.text = str(selected_wall.rect.centery)
                elif key == "width":
                    text_input.text = str(selected_wall.rect.width)
                elif key == "height":
                    text_input.text = str(selected_wall.rect.height)
                text_input.txt_surface = text_input.font.render(
                    text_input.text, True, text_input.color
                )
    else:
        # Clear text inputs when no wall is selected
        for text_input in text_inputs.values():
            if not text_input.active:
                text_input.text = ""
                text_input.txt_surface = text_input.font.render(
                    text_input.text, True, text_input.color
                )

    # Draw text inputs
    for text_input in text_inputs.values():
        text_input.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
