import pygame
from operations.transformations import Transformation

class RightTriangle:
    def __init__(self, points, color):
        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            self.points = [
                (x1, y1),
                (x2, y1),
                (x1, y2)
            ]
        else:
            self.points = points
            
        self.color = color
        self.position = self.calculate_center()
        self.selected = False
    
    def calculate_center(self):
        x = sum(p[0] for p in self.points) / len(self.points)
        y = sum(p[1] for p in self.points) / len(self.points)
        return (x, y)
    
    def contains_point(self, point):
        # Упрощенная проверка попадания точки в треугольник
        x, y = point
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        x3, y3 = self.points[2]
        
        area = 0.5 * abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1))
        area1 = 0.5 * abs((x1-x)*(y2-y) - (x2-x)*(y1-y))
        area2 = 0.5 * abs((x2-x)*(y3-y) - (x3-x)*(y2-y))
        area3 = 0.5 * abs((x3-x)*(y1-y) - (x1-x)*(y3-y))
        
        return abs(area - (area1 + area2 + area3)) < 0.1
    
    def intersects(self, other):
        """Проверка пересечения с другим полигоном или треугольником"""
        from operations.tmo import TMOperations  # Локальный импорт
        for i in range(len(self.points)):
            for j in range(len(other.points)):
                if TMOperations.lines_intersect(self.points[i], self.points[(i + 1) % len(self.points)],
                                                  other.points[j], other.points[(j + 1) % len(other.points)]):
                    return True
        return False
    
    def move(self, offset):
        dx = offset[0] - self.position[0]
        dy = offset[1] - self.position[1]
        self.points = [(p[0] + dx, p[1] + dy) for p in self.points]
        self.position = offset
    
    def rotate(self, angle, center):
        self.points = [Transformation.rotate_point(p, angle, center) for p in self.points]
        self.position = self.calculate_center()
    
    def scale_x(self, sx, center):
        self.points = [Transformation.scale_point(p, (sx, 1), center) for p in self.points]
        self.position = self.calculate_center()
    
    def scale_xy(self, scale, center):
        self.points = [Transformation.scale_point(p, (scale, scale), center) for p in self.points]
        self.position = self.calculate_center()
    
    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.points)
        pygame.draw.polygon(surface, (0, 0, 0), self.points, 1)
    
    def draw_selection(self, surface):
        for point in self.points:
            pygame.draw.circle(surface, (255, 0, 0), point, 6, 2)