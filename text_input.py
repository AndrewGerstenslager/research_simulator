import pygame


# Define text input for clock rate
class TextInput:
    """
    A class to handle text input in Pygame.

    This class creates a text input field that can be interacted with using
    mouse clicks and keyboard input.
    """

    def __init__(
        self, x: int, y: int, width: int, height: int, initial_text: str = ""
    ) -> None:
        """
        Initialize the TextInput object.

        Args:
            x (int): The x-coordinate of the input field.
            y (int): The y-coordinate of the input field.
            width (int): The width of the input field.
            height (int): The height of the input field.
            initial_text (str, optional): The initial text in the input field. Defaults to "".
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color("lightskyblue3")
        self.text = initial_text
        self.font = pygame.font.Font(None, 24)
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # Blink every 500ms

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle Pygame events for the text input.

        Args:
            event (pygame.event.Event): The Pygame event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (
                pygame.Color("dodgerblue2")
                if self.active
                else pygame.Color("lightskyblue3")
            )
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = pygame.Color("lightskyblue3")
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self) -> None:
        """Update the width of the input box if the text surface is larger than the box."""
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

        # Update cursor blink
        if pygame.time.get_ticks() - self.cursor_timer > self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = pygame.time.get_ticks()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the text input on the screen.

        Args:
            screen (pygame.Surface): The Pygame surface to draw on.
        """
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

        # Draw cursor when active
        if self.active and self.cursor_visible:
            cursor_pos = self.rect.x + 5 + self.txt_surface.get_width()
            cursor_rect = pygame.Rect(
                cursor_pos, self.rect.y + 5, 2, self.font.get_height()
            )
            pygame.draw.rect(screen, self.color, cursor_rect)

    def get_text(self) -> str:
        """
        Get the current text in the input field.

        Returns:
            str: The current text in the input field.
        """
        return self.text
