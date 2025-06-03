import pygame 
import math 
import numpy as np 
from typing import List, Tuple, Union 
 
class Primitives: 
    def __init__(self, color: Tuple[int, int, int], line_width: int = 1): 
        self.points: List[Tuple[float, float]] = [] 
        self.color = color 
        self.selected = False 
        self.line_width = line_width 
        self.center = (0, 0) 
        self.update_center() 
 
    def update_center(self): 
        """Вычисление центра фигуры как среднего арифметического вершин""" 
        if not self.points: 
            return (0, 0) 
         
        sum_x = sum(p[0] for p in self.points) 
        sum_y = sum(p[1] for p in self.points) 
        self.center = (sum_x / len(self.points), sum_y / len(self.points)) 
        return self.center 

 
 
    def contains_point(self, point: Tuple[float, float]) -> bool: 
        """Проверка, находится ли точка внутри полигона (алгоритм ray casting)""" 
        if len(self.points) < 3: 
            return False 
             
        x, y = point 
        n = len(self.points) 
        inside = False 
        p1x, p1y = self.points[0] 
         
        for i in range(n + 1): 
            p2x, p2y = self.points[i % n] 
            if y > min(p1y, p2y): 
                if y <= max(p1y, p2y): 
                    if x <= max(p1x, p2x): 
                        if p1y != p2y: 
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x 
                        if p1x == p2x or x <= xinters: 
                            inside = not inside 
            p1x, p1y = p2x, p2y 
             
        return inside 
 
    def matrix_multiply(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray: 
        """Умножение матрицы на вектор""" 
        return matrix @ vector 
 
    def move(self, dx: float, dy: float): 
        """Плоскопараллельное перемещение""" 
        self.points = [(x + dx, y + dy) for x, y in self.points] 
        self.update_center() 
 
    def rotate(self, angle: float, center: Tuple[float, float] = None): 
        """Поворот вокруг центра фигуры или заданной точки""" 
        center = center or self.center 
        angle_rad = math.radians(angle) 
        cos_a = math.cos(angle_rad) 
        sin_a = math.sin(angle_rad) 
         
        # Матрица поворота 
        rotation_matrix = np.array([ 
            [cos_a, -sin_a, 0], 
            [sin_a,  cos_a, 0], 
            [0,      0,     1] 
        ]) 
         
        # Перенос в начало координат 
        translate_to_origin = np.array([ 
            [1, 0, -center[0]], 
            [0, 1, -center[1]], 
            [0, 0,  1] 
        ]) 
         
        # Обратный перенос 
        translate_back = np.array([ 
            [1, 0, center[0]], 
            [0, 1, center[1]], 
            [0, 0, 1] 
        ]) 
         
        # Комбинированная матрица преобразования 

 
        transform_matrix = translate_back @ rotation_matrix @ translate_to_origin 
         
        # Применение преобразования к точкам 
        new_points = [] 
        for point in self.points: 
            # Конвертация в однородные координаты 
            vector = np.array([point[0], point[1], 1]) 
            # Умножение на матрицу преобразования 
            transformed = self.matrix_multiply(transform_matrix, vector) 
            new_points.append((transformed[0], transformed[1])) 
         
        self.points = new_points 
        self.update_center() 
 
    def scale(self, sx: float, sy: float, center: Tuple[float, float] = None): 
        """Масштабирование относительно центра или заданной точки""" 
        center = center or self.center 
         
        # Матрица масштабирования 
        scale_matrix = np.array([ 
            [sx, 0,  0], 
            [0,  sy, 0], 
            [0,  0,  1] 
        ]) 
         
        # Перенос в начало координат 
        translate_to_origin = np.array([ 
            [1, 0, -center[0]], 
            [0, 1, -center[1]], 
            [0, 0,  1] 
        ]) 
         
        # Обратный перенос 
        translate_back = np.array([ 
            [1, 0, center[0]], 
            [0, 1, center[1]], 
            [0, 0, 1] 
        ]) 
         
        # Комбинированная матрица преобразования 
        transform_matrix = translate_back @ scale_matrix @ translate_to_origin 
         
        # Применение преобразования к точкам 
        new_points = [] 
        for point in self.points: 
            vector = np.array([point[0], point[1], 1]) 
            transformed = self.matrix_multiply(transform_matrix, vector) 
            new_points.append((transformed[0], transformed[1])) 
         
        self.points = new_points 
        self.update_center() 
 
    def reflect(self, line_points: List[Tuple[float, float]]): 
        """Зеркальное отражение относительно прямой общего положения""" 
        if len(line_points) < 2: 
            return 
             
        # Расчет угла наклона прямой 
        dx = line_points[1][0] - line_points[0][0] 
        dy = line_points[1][1] - line_points[0][1] 
        angle_rad = math.atan2(dy, dx) 
        angle_deg = math.degrees(angle_rad) 
         

 
        # Центр линии отражения 
        line_center = ( 
            (line_points[0][0] + line_points[1][0]) / 2, 
            (line_points[0][1] + line_points[1][1]) / 2 
        ) 
         
        # Последовательность преобразований: 
        self.move(-line_center[0], -line_center[1]) 
        self.rotate(-angle_deg, (0, 0)) 
        self.rotate(180, (0, 0)) 
        self.scale(-1, 1, (0, 0)) 
        self.rotate(angle_deg, (0, 0)) 
        self.move(line_center[0], line_center[1]) 
 
    def draw(self, surface: pygame.Surface): 
        """Отрисовка примитива с заливкой (алгоритм сканирующих строк)""" 
        if len(self.points) < 3: 
            return 
             
        # Поиск min и max Y 
        y_min = min(p[1] for p in self.points) 
        y_max = max(p[1] for p in self.points) 
         
        # Отрисовка по сканирующим строкам 
        for y in range(int(y_min), int(y_max) + 1): 
            intersections = [] 
             
            # Поиск пересечений с ребрами 
            for i in range(len(self.points)): 
                p1 = self.points[i] 
                p2 = self.points[(i + 1) % len(self.points)] 
                 
                if (p1[1] < y and p2[1] >= y) or (p2[1] < y and p1[1] >= y): 
                    if p1[1] != p2[1]: 
                        x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - 
p1[1]) 
                        intersections.append(x) 
             
            intersections.sort() 
             
            # Отрисовка горизонтальных линий между точками пересечения 
            for i in range(0, len(intersections), 2): 
                if i + 1 < len(intersections): 
                    start_x = int(intersections[i]) 
                    end_x = int(intersections[i + 1]) 
                    pygame.draw.line(surface, self.color, (start_x, y), (end_x, 
y), self.line_width) 
 
    def draw_outline(self, surface: pygame.Surface): 
        """Отрисовка контура примитива""" 
        if len(self.points) > 1: 
            pygame.draw.polygon(surface, (0, 0, 0), self.points, self.line_width) 
 
    def draw_selection(self, surface: pygame.Surface): 
        """Отрисовка выделения (красные кружки в вершинах)""" 
        for point in self.points: 
            pygame.draw.circle(surface, (255, 0, 0), (int(point[0]), 
int(point[1])), 5, 1) 