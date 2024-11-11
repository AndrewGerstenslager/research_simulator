# %%
import pygame
import json
import sys
from tkinter import Tk, filedialog
from wall import Wall
from button import Button
from constants import *
from text_input import TextInput

pygame.init()

# Create text inputs for wall properties
text_inputs = {
    "x": TextInput(1000, 50, 150, 30, ""),
    "y": TextInput(1000, 120, 150, 30, ""),
    "width": TextInput(1000, 190, 150, 30, ""),
    "height": TextInput(1000, 260, 150, 30, ""),
}


def apply_wall_properties():
    global selected_wall
    if selected_wall:
        try:
            # Store original values
            original_rect = selected_wall.rect.copy()

            # Get new values
            x = int(text_inputs["x"].text)
            y = int(text_inputs["y"].text)
            width = int(text_inputs["width"].text)
            height = int(text_inputs["height"].text)

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


# Screen setup
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Wall Editor")
selected_wall = None
copied_wall = None
is_dragging = False
walls = []


def save_walls():
    root = Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("JSON files", "*.json")]
    )
    if filename:
        with open(filename, "w") as f:
            json.dump([wall.to_dict() for wall in walls], f)
    root.destroy()


def load_walls():
    global walls
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        defaultextension=".json", filetypes=[("JSON files", "*.json")]
    )
    if filename:
        with open(filename, "r") as f:
            walls = [Wall.from_dict(data) for data in json.load(f)]
    root.destroy()


def reset_world():
    global walls
    walls = []


def delete_selected_wall():
    global walls, selected_wall
    if selected_wall:
        walls.remove(selected_wall)
        selected_wall = None


def handle_mouse_events(event):
    # Handle text input events
    for text_input in text_inputs.values():
        text_input.handle_event(event)
    global selected_wall, copied_wall, is_dragging
    if event.type == pygame.MOUSEBUTTONDOWN:
        is_dragging = False
        for button in buttons:
            if button.is_clicked(event.pos):
                button.action()
                return
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
            save_walls()
        elif event.key == pygame.K_l:
            load_walls()


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
    Button(850, 50, 100, 50, "Add Wall", spawn_wall),
    Button(850, 110, 100, 50, "Copy Wall", copy_wall),
    Button(
        850,
        170,
        100,
        50,
        "Paste Wall",
        paste_wall,
        color=DISABLED_GRAY if not copied_wall else BLACK,
    ),
    Button(850, 230, 100, 50, "Reset World", reset_world),
    Button(850, 290, 100, 50, "Delete Wall", delete_selected_wall),
    Button(850, 350, 100, 50, "Save World", save_walls),
    Button(850, 410, 100, 50, "Load World", load_walls),
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

    # Draw the buttons
    for button in buttons:
        button.color = (
            DISABLED_GRAY if button.text == "Paste Wall" and not copied_wall else BLACK
        )
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
