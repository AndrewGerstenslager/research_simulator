# %%
import pygame
import json
import sys
from tkinter import Tk, filedialog
from wall import Wall
from button import Button
from constants import *

pygame.init()

# Screen setup
screen = pygame.display.set_mode((1000, 600))
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
            selected_wall.rect.x += event.rel[0]
            selected_wall.rect.y += event.rel[1]


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
        wall.draw(screen)

    # Draw the buttons
    for button in buttons:
        button.color = (
            DISABLED_GRAY if button.text == "Paste Wall" and not copied_wall else BLACK
        )
        button.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
