import math 
from typing import List, Tuple 
PointF = Tuple[float, float] 
class Line: 
    def __init__(self, points: List[PointF], color=None): 
        self.points = points  # список точек (вершин линии) 
        self.color = color    
# цвет линии (не используется в коде, но можно добавить 
    def calculate_center(self) -> PointF: 
        sum_x = sum(p[0] for p in self.points) 
        sum_y = sum(p[1] for p in self.points) 
        count = len(self.points) 
        return (sum_x / count, sum_y / count) 
    def move(self, dx: float, dy: float): 
        self.points = [(x + dx, y + dy) for (x, y) in self.points] 
    def scale(self, scale_x: float, scale_y: float, center: PointF = None): 
        if center is None: 
            center = self.calculate_center() 
            cx, cy = center 
            scaled_points = [] 
        for (x, y) in self.points: 
            x_new = cx + scale_x * (x - cx) 
            y_new = cy + scale_y * (y - cy) 
            scaled_points.append((x_new, y_new)) 
            self.points = scaled_points 

    def rotate(self, angle_degrees: float, center: PointF = None): 
        if center is None: 
            center = self.calculate_center() 
        cx, cy = center 
        angle_radians = math.radians(angle_degrees) 
        cos_a = math.cos(angle_radians) 
        sin_a = math.sin(angle_radians) 
 
        rotated_points = [] 
        for (x, y) in self.points: 
            # переносим точку в начало координат 
            x_shifted = x - cx 
            y_shifted = y - cy 
            # поворот 
            x_rot = x_shifted * cos_a - y_shifted * sin_a 
            y_rot = x_shifted * sin_a + y_shifted * cos_a 
            # перенос обратно 
            x_new = x_rot + cx 
            y_new = y_rot + cy 
            rotated_points.append((x_new, y_new)) 
        self.points = rotated_points 
 
    def reflect(self, mirror_line: List[PointF]): 
        # Отражение относительно произвольной прямой, заданной двумя точками 
        mirror_line = [p1, p2] 
        p1, p2 = mirror_line 
        dx = p2[0] - p1[0] 
        dy = p2[1] - p1[1] 
        length = math.hypot(dx, dy) 
        if length == 0: 
            return  # Нельзя отражать относительно точки 
 
        # Нормализуем вектор прямой 
        ux = dx / length 
        uy = dy / length 
 
        reflected_points = [] 
        for (x, y) in self.points: 
            # Вектор от p1 к точке 
            vx = x - p1[0] 
            vy = y - p1[1] 
            # Проекция вектора на прямую 
            proj = vx * ux + vy * uy 
            # Координаты проекции на прямой 
            proj_x = p1[0] + proj * ux 
            proj_y = p1[1] + proj * uy 
            # Вектор от точки до проекции 
            dx_perp = proj_x - x 
            dy_perp = proj_y - y 
            # Отражённая точка 
            x_ref = x + 2 * dx_perp 
            y_ref = y + 2 * dy_perp 
            reflected_points.append((x_ref, y_ref)) 
        self.points = reflected_points 
 
    def point_inside(self, x: float, y: float) -> bool: 
        # Проверка, находится ли точка (x, y) внутри многоугольника (алгоритм "луча") 
        n = len(self.points) 
        inside = False 
        j = n - 1 
        for i in range(n): 
            xi, yi = self.points[i] 
            xj, yj = self.points[j] 
            intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi) 
            if intersect: 
                inside = not inside 
 
            j = i 
        return inside