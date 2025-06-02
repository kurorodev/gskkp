import pygame

class ColorPalette:
    def __init__(self, x, y, colors):
        self.x = x
        self.y = y
        self.colors = colors
        self.size = 20
        self.rect = pygame.Rect(x, y, len(colors) * (self.size + 5) + 5, self.size + 10)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if self.rect.collidepoint(x, y):
                index = (x - self.x) // (self.size + 5)
                if 0 <= index < len(self.colors):
                    return self.colors[index]
        return None
        
    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)
        
        for i, color in enumerate(self.colors):
            x_pos = self.x + i * (self.size + 5) + 5
            pygame.draw.rect(surface, color, (x_pos, self.y + 5, self.size, self.size))
            pygame.draw.rect(surface, (0, 0, 0), (x_pos, self.y + 5, self.size, self.size), 1)