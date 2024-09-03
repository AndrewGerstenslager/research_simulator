import pygame


# Define text input for clock rate
class TextInput:
    def __init__(self, x, y, width, height, initial_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = pygame.Color("lightskyblue3")
        self.text = initial_text
        self.font = pygame.font.Font(None, 24)
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False

    def handle_event(self, event):
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

    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text
