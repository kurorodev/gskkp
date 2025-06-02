import numpy as np
from primitives.polygon import Polygon
from shapely.geometry import Polygon as ShapelyPolygon

class TMOperations:
    
    @staticmethod
    def union(poly1, poly2):
        shapely_poly1 = ShapelyPolygon(poly1.points)
        shapely_poly2 = ShapelyPolygon(poly2.points)
        union_result = shapely_poly1.union(shapely_poly2)

        if union_result.is_empty:
            return None

        if union_result.geom_type == 'Polygon':
            return Polygon(list(union_result.exterior.coords), poly1.color)
        elif union_result.geom_type == 'MultiPolygon':
            # Можно выбрать первую или объединить все
            largest = max(union_result.geoms, key=lambda g: g.area)
            return Polygon(list(largest.exterior.coords), poly1.color)


    @staticmethod
    def symmetric_difference(poly1, poly2):
        """Полноценная реализация симметрической разности двух полигонов с использованием Shapely"""
        shapely_poly1 = ShapelyPolygon(poly1.points)
        shapely_poly2 = ShapelyPolygon(poly2.points)
        sym_diff_result = shapely_poly1.symmetric_difference(shapely_poly2)

        if sym_diff_result.is_empty:
            return None

        if sym_diff_result.geom_type == 'Polygon':
            return Polygon(list(sym_diff_result.exterior.coords), poly1.color)

        elif sym_diff_result.geom_type == 'MultiPolygon':
            # Объединяем все части в одну (можно вернуть список, если это нужно)
            all_points = []
            for geom in sym_diff_result.geoms:
                all_points.extend(list(geom.exterior.coords))
            return Polygon(all_points, poly1.color)


    @staticmethod
    def intersects(poly1, poly2):
        """Проверка пересечения двух полигонов"""
        for i in range(len(poly1.points)):
            for j in range(len(poly2.points)):
                if TMOperations.lines_intersect(poly1.points[i], poly1.points[(i + 1) % len(poly1.points)],
                                                  poly2.points[j], poly2.points[(j + 1) % len(poly2.points)]):
                    return True
        return False

    @staticmethod
    def get_intersection_points(poly1, poly2):
        """Получение точек пересечения двух полигонов"""
        intersection_points = []
        for i in range(len(poly1.points)):
            for j in range(len(poly2.points)):
                intersection = TMOperations.line_intersection(poly1.points[i], poly1.points[(i + 1) % len(poly1.points)],
                                                              poly2.points[j], poly2.points[(j + 1) % len(poly2.points)])
                if intersection:
                    intersection_points.append(intersection)
        return intersection_points

    @staticmethod
    def lines_intersect(p1, p2, p3, p4):
        """Проверка пересечения двух отрезков"""
        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # коллинеарные
            return 1 if val > 0 else 2  # 1 - по часовой, 2 - против часовой

        o1 = orientation(p1, p2, p3)
        o2 = orientation(p1, p2, p4)
        o3 = orientation(p3, p4, p1)
        o4 = orientation(p3, p4, p2)

        if o1 != o2 and o3 != o4:
            return True  # Пересекаются

        return False  # Не пересекаются
    
    @staticmethod
    def line_intersection(p1, p2, p3, p4):
        """Находит точку пересечения двух отрезков, если она существует."""
        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # коллинеарные
            return 1 if val > 0 else 2  # 1 - по часовой, 2 - против часовой

        o1 = orientation(p1, p2, p3)
        o2 = orientation(p1, p2, p4)
        o3 = orientation(p3, p4, p1)
        o4 = orientation(p3, p4, p2)

        # Общий случай
        if o1 != o2 and o3 != o4:
            # Вычисляем точку пересечения
            denom = (p2[1] - p1[1]) * (p4[0] - p3[0]) - (p2[0] - p1[0]) * (p4[1] - p3[1])
            if denom == 0:
                return None  # Параллельные линии

            x = ((p2[0] - p1[0]) * (p4[0] * p3[1] - p4[1] * p3[0]) - (p4[0] - p3[0]) * (p2[0] * p1[1] - p2[1] * p1[0])) / denom
            y = ((p2[1] - p1[1]) * (p4[0] * p3[1] - p4[1] * p3[0]) - (p4[0] - p3[0]) * (p2[1] * p1[0] - p2[0] * p1[1])) / denom
            return (x, y)

        return None  # Нет пересечения


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
