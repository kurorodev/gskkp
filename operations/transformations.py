import math
import numpy as np

class Transformation:
    @staticmethod
    def rotate_point(point, angle, center):
        """Поворот точки вокруг центра"""
        x, y = point
        cx, cy = center
        angle_rad = math.radians(angle)
        
        # Перенос в начало координат
        x_temp = x - cx
        y_temp = y - cy
        
        # Поворот
        x_rot = x_temp * math.cos(angle_rad) - y_temp * math.sin(angle_rad)
        y_rot = x_temp * math.sin(angle_rad) + y_temp * math.cos(angle_rad)
        
        # Обратный перенос
        return (x_rot + cx, y_rot + cy)
    
    @staticmethod
    def scale_point(point, scale, center):
        """Масштабирование точки относительно центра"""
        x, y = point
        cx, cy = center
        sx, sy = scale
        
        # Перенос в начало координат
        x_temp = x - cx
        y_temp = y - cy
        
        # Масштабирование
        x_scaled = x_temp * sx
        y_scaled = y_temp * sy
        
        # Обратный перенос
        return (x_scaled + cx, y_scaled + cy)
    
    @staticmethod
    def calculate_angle(center, target):
        """Вычисление угла поворота между двумя точками"""
        dx = target[0] - center[0]
        dy = target[1] - center[1]
        return math.degrees(math.atan2(dy, dx))
    
    @staticmethod
    def calculate_scale(center, target, axis):
        """Вычисление коэффициента масштабирования"""
        dx = target[0] - center[0]
        dy = target[1] - center[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        if axis == 'x':
            return max(0.1, abs(dx / 50))
        elif axis == 'xy':
            return max(0.1, dist / 50)
        return 1.0