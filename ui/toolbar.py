import pygame

class Toolbar:
    def __init__(self, x, y, tools):
        self.x = x
        self.y = y
        self.tools = tools
        self.button_size = 50
        self.height = len(tools) * (self.button_size + 5) + 10
        self.rect = pygame.Rect(x, y, 100, self.height)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if self.rect.collidepoint(x, y):
                index = (y - self.y) // (self.button_size + 5)
                if 0 <= index < len(self.tools):
                    return self.tools[index][0]
        return None
        
    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)
        
        font = pygame.font.SysFont(None, 24)
        for i, (_, name) in enumerate(self.tools):
            y_pos = self.y + i * (self.button_size + 5) + 10
            text = font.render(name, True, (0, 0, 0))
            surface.blit(text, (self.x + 10, y_pos))