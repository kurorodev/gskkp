import pygame
import numpy as np
from primitives.polygon import Polygon

class TMOperations:
    @staticmethod
    def union(poly1, poly2):
        # Упрощенная реализация объединения
        all_points = poly1.points + poly2.points
        hull = TMOperations.convex_hull(all_points)
        if hull:
            return Polygon(hull, poly1.color)
        return None

    @staticmethod
    def symmetric_difference(poly1, poly2):
        # Упрощенная реализация симметрической разности
        points = []
        for p in poly1.points:
            if not poly2.contains_point(p):
                points.append(p)
        
        for p in poly2.points:
            if not poly1.contains_point(p):
                points.append(p)
        
        if len(points) >= 3:
            hull = TMOperations.convex_hull(points)
            if hull:
                return Polygon(hull, poly1.color)
        return None

    @staticmethod
    def convex_hull(points):
        """Алгоритм Грэхема для построения выпуклой оболочки"""
        if len(points) < 3:
            return None
            
        # Находим точку с минимальной y-координатой
        start = min(points, key=lambda p: (p[1], p[0]))
        
        # Сортируем точки по полярному углу
        sorted_points = sorted(points, key=lambda p: (
            np.arctan2(p[1]-start[1], p[0]-start[0])
        ))
        
        # Построение выпуклой оболочки
        hull = []
        for p in sorted_points:
            while len(hull) >= 2 and TMOperations.cross(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)
        
        return hull

    @staticmethod
    def cross(o, a, b):
        return (a[0]-o[0]) * (b[1]-o[1]) - (a[1]-o[1]) * (b[0]-o[0])