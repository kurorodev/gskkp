import pygame
from operations.transformations import Transformation


class Polygon:
    def __init__(self, points, color):
        self.points = points
        self.color = color
        self.position = self.calculate_center()
        self.selected = False
    
    def calculate_center(self):
        x = sum(p[0] for p in self.points) / len(self.points)
        y = sum(p[1] for p in self.points) / len(self.points)
        return (x, y)
    
    def contains_point(self, point):
        # Проверка попадания точки в полигон
        x, y = point
        n = len(self.points)
        inside = False
        p1x, p1y = self.points[0]
        for i in range(n+1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def intersects(self, other):
        from operations.tmo import TMOperations
        """Проверка пересечения с другим полигоном"""
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