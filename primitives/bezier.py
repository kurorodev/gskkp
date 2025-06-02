import pygame
import numpy as np
from operations.transformations import Transformation

class BezierCurve:
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
        for p in self.points:
            if np.linalg.norm(np.array(p) - np.array(point)) < 10:
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
        # Рисование контрольных точек
        for point in self.points:
            pygame.draw.circle(surface, (100, 100, 100), point, 4)
        
        # Рисование кривой
        if len(self.points) == 4:
            t = np.linspace(0, 1, 100)
            curve_points = []
            for ti in t:
                x = (1-ti)**3 * self.points[0][0] + 3*(1-ti)**2*ti*self.points[1][0] + \
                     3*(1-ti)*ti**2*self.points[2][0] + ti**3*self.points[3][0]
                y = (1-ti)**3 * self.points[0][1] + 3*(1-ti)**2*ti*self.points[1][1] + \
                     3*(1-ti)*ti**2*self.points[2][1] + ti**3*self.points[3][1]
                curve_points.append((x, y))
            
            if len(curve_points) > 1:
                pygame.draw.lines(surface, self.color, False, curve_points, 2)
    
    def draw_selection(self, surface):
        for point in self.points:
            pygame.draw.circle(surface, (255, 0, 0), point, 6, 2)