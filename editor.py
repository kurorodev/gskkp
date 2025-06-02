import pygame
from ui.toolbar import Toolbar
from ui.palette import ColorPalette
from operations.tmo import TMOperations
from operations.transformations import Transformation
from primitives.bezier import BezierCurve
from primitives.polygon import Polygon
from primitives.right_triangle import RightTriangle

class GraphicsEditor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Векторный графический редактор (Вариант 78)")
        
        self.background = (240, 240, 240)
        self.objects = []
        self.selected_object = None
        self.dragging = False
        self.current_tool = "select"
        self.current_color = (0, 0, 0)
        self.temp_points = []
        
        # Инициализация компонентов UI
        self.toolbar = Toolbar(10, 10, [
            ("select", "Выделение"),
            ("bezier", "Кривая Безье"),
            ("triangle", "Треугольник"),
            ("polygon", "Многоугольник"),
            ("union", "Объединение (∪)"),
            ("sym_diff", "Симм.разность (⊕)"),
            ("rotate", "Поворот (Rc)"),
            ("scale_x", "Масшт.X (Sxc)"),
            ("scale_xy", "Масшт.XY (Sxyf)"),
            ("move", "Перемещение")
        ])
        
        self.palette = ColorPalette(self.width - 200, 10, [
            (0, 0, 0), (255, 0, 0), (0, 255, 0), 
            (0, 0, 255), (255, 255, 0), (128, 0, 128)
        ])
        
        self.font = pygame.font.SysFont(None, 24)
        self.status = "Готов"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Обработка UI
            tool = self.toolbar.handle_event(event)
            if tool:
                self.current_tool = tool
                self.temp_points = []
                self.status = f"Выбран инструмент: {tool}"
                
            color = self.palette.handle_event(event)
            if color:
                self.current_color = color
                if self.selected_object:
                    self.selected_object.color = color
                self.status = f"Выбран цвет: {color}"
                
            # Обработка мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)
                
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
                
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.handle_drag(event)
                
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event)
                
        return True

    def handle_mouse_down(self, event):
        x, y = event.pos
        if self.toolbar.rect.collidepoint(x, y) or self.palette.rect.collidepoint(x, y):
            return
            
        # Выбор объекта
        if self.current_tool == "select":
            self.selected_object = None
            for obj in reversed(self.objects):
                if obj.contains_point((x, y)):
                    self.selected_object = obj
                    self.status = f"Выбран объект: {type(obj).__name__}"
                    break
        
        # Создание кривой Безье
        elif self.current_tool == "bezier":
            if len(self.temp_points) < 4:
                self.temp_points.append((x, y))
                self.status = f"Точка {len(self.temp_points)}/4"
                if len(self.temp_points) == 4:
                    self.objects.append(BezierCurve(self.temp_points, self.current_color))
                    self.temp_points = []
                    self.status = "Кривая Безье создана"
        
        # Создание треугольника
        elif self.current_tool == "triangle":
            if len(self.temp_points) < 2:
                self.temp_points.append((x, y))
                self.status = f"Точка {len(self.temp_points)}/2"
                if len(self.temp_points) == 2:
                    self.objects.append(RightTriangle(self.temp_points, self.current_color))
                    self.temp_points = []
                    self.status = "Треугольник создан"
        
        # Создание многоугольника
        elif self.current_tool == "polygon":
            if event.button == 1:  # ЛКМ
                self.temp_points.append((x, y))
                self.status = f"Вершина {len(self.temp_points)}. Enter - завершить"
            elif event.button == 3:  # ПКМ
                if len(self.temp_points) >= 3:
                    self.objects.append(Polygon(self.temp_points, self.current_color))
                    self.temp_points = []
                    self.status = "Многоугольник создан"
        
        # Начало перемещения
        elif self.current_tool == "move" and self.selected_object:
            self.dragging = True
            self.drag_offset = (x - self.selected_object.position[0], 
                              y - self.selected_object.position[1])
        
        # Точки для операций
        elif self.current_tool in ["rotate", "scale_x", "scale_xy"]:
            self.temp_points.append((x, y))
            if len(self.temp_points) == 1:
                self.status = "Укажите центр преобразования"
            elif len(self.temp_points) == 2 and self.selected_object:
                self.apply_transformation()

    def handle_drag(self, event):
        if self.selected_object and self.current_tool == "move":
            x, y = event.pos
            new_x = x - self.drag_offset[0]
            new_y = y - self.drag_offset[1]
            self.selected_object.move((new_x, new_y))

    def handle_key_down(self, event):
        # Завершение создания многоугольника
        if event.key == pygame.K_RETURN and self.current_tool == "polygon":
            if len(self.temp_points) >= 3:
                self.objects.append(Polygon(self.temp_points, self.current_color))
                self.temp_points = []
                self.status = "Многоугольник создан"
        
        # Удаление объекта
        elif event.key == pygame.K_DELETE and self.selected_object:
            self.objects.remove(self.selected_object)
            self.selected_object = None
            self.status = "Объект удален"
        
        # Отмена операции
        elif event.key == pygame.K_ESCAPE:
            self.temp_points = []
            self.status = "Операция отменена"

    def apply_transformation(self):
        if not self.selected_object or len(self.temp_points) < 2:
            return
            
        center = self.temp_points[0]
        target = self.temp_points[1]
        
        if self.current_tool == "rotate":
            angle = Transformation.calculate_angle(center, target)
            self.selected_object.rotate(angle, center)
            self.status = f"Поворот на {int(angle)}°"
        
        elif self.current_tool == "scale_x":
            sx = Transformation.calculate_scale(center, target, 'x')
            self.selected_object.scale_x(sx, center)
            self.status = f"Масштаб по X: {sx:.1f}"
        
        elif self.current_tool == "scale_xy":
            scale = Transformation.calculate_scale(center, target, 'xy')
            self.selected_object.scale_xy(scale, center)
            self.status = f"Масштаб XY: {scale:.1f}"
        
        self.temp_points = []

    def apply_tmo_operation(self):
        selected = [obj for obj in self.objects if obj.selected]
        if len(selected) == 2:
            result = TMOperations.union(selected[0], selected[1]) \
                if self.current_tool == "union" \
                else TMOperations.symmetric_difference(selected[0], selected[1])
            
            if result:
                self.objects.append(result)
                for obj in selected:
                    obj.selected = False
                    self.objects.remove(obj)
                self.selected_object = result
                self.status = "TMO применена"

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            
            # Применение TMO после выбора объектов
            if self.current_tool in ["union", "sym_diff"]:
                self.apply_tmo_operation()
                self.current_tool = "select"
            
            # Отрисовка
            self.screen.fill(self.background)
            
            # Сетка
            for x in range(0, self.width, 20):
                pygame.draw.line(self.screen, (220, 220, 220), (x, 0), (x, self.height))
            for y in range(0, self.height, 20):
                pygame.draw.line(self.screen, (220, 220, 220), (0, y), (self.width, y))
            
            # Объекты
            for obj in self.objects:
                obj.draw(self.screen)
            
            # Временные точки
            for point in self.temp_points:
                pygame.draw.circle(self.screen, (255, 0, 0), point, 5)
            
            # Контур выделенного объекта
            if self.selected_object:
                self.selected_object.draw_selection(self.screen)
            
            # UI
            self.toolbar.draw(self.screen)
            self.palette.draw(self.screen)
            
            # Статус
            status_surface = self.font.render(self.status, True, (0, 0, 0))
            self.screen.blit(status_surface, (10, self.height - 30))
            
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()