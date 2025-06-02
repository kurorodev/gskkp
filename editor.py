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
        self.selected_objects = []
        self.dragging = False
        self.current_tool = "select"
        self.current_color = (0, 0, 0)
        self.temp_points = []

        self.toolbar = Toolbar(20, 20, [
            ("select", "Выделение"),
            ("bezier", "Кривая Безье"),
            ("triangle", "Треугольник"),
            ("polygon", "Многоугольник"),
            ("union", "Объединение"),
            ("sym_diff", "Симм.разность"),
            ("rotate", "Поворот (Rc)"),
            ("scale_x", "Масшт.X (Sxc)"),
            ("scale_xy", "Масшт.XY (Sxyf)"),
            ("move", "Перемещение"),
            ("clear", "Очистить экран")  # Добавляем кнопку очистки
        ])

        self.palette = ColorPalette(self.width - 200, 10, [
            (0, 0, 0), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (128, 0, 128)
        ])

        self.font = pygame.font.SysFont(None, 24)
        self.status = "Готов"

    def clear_screen(self):
        """Удаляет все объекты с холста и сбрасывает выделение."""
        self.objects.clear()
        self.selected_objects.clear()
        self.status = "Экран очищен"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            tool = self.toolbar.handle_event(event)
            if tool:
                self.current_tool = tool
                self.temp_points = []
                self.status = f"Выбран инструмент: {tool}"

                # Обработка нажатия кнопки очистки
                if tool == "clear":
                    self.clear_screen()

            color = self.palette.handle_event(event)
            if color:
                self.current_color = color
                for obj in self.selected_objects:
                    obj.color = color
                self.status = f"Выбран цвет: {color}"

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

        if self.current_tool == "select":
            if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.selected_objects = []

            for obj in reversed(self.objects):
                if obj.contains_point((x, y)):
                    if obj not in self.selected_objects:
                        self.selected_objects.append(obj)
                    else:
                        self.selected_objects.remove(obj)
                    break
            self.status = f"Выбрано объектов: {len(self.selected_objects)}"

        elif self.current_tool == "bezier":
            self.temp_points.append((x, y))
            if len(self.temp_points) == 4:
                self.objects.append(BezierCurve(self.temp_points, self.current_color))
                self.temp_points = []
                self.status = "Кривая Безье создана"
            else:
                self.status = f"Точка {len(self.temp_points)}/4"

        elif self.current_tool == "triangle":
            self.temp_points.append((x, y))
            if len(self.temp_points) == 2:
                self.objects.append(RightTriangle(self.temp_points, self.current_color))
                self.temp_points = []
                self.status = "Треугольник создан"
            else:
                self.status = f"Точка {len(self.temp_points)}/2"

        elif self.current_tool == "polygon":
            if event.button == 1:
                self.temp_points.append((x, y))
                self.status = f"Вершина {len(self.temp_points)}. Enter - завершить"
            elif event.button == 3:
                if len(self.temp_points) >= 3:
                    self.objects.append(Polygon(self.temp_points, self.current_color))
                    self.temp_points = []
                    self.status = "Многоугольник создан"

        elif self.current_tool == "move" and self.selected_objects:
            self.dragging = True
            self.drag_offset = [(x - obj.position[0], y - obj.position[1]) for obj in self.selected_objects]

        elif self.current_tool in ["rotate", "scale_x", "scale_xy"]:
            self.temp_points.append((x, y))
            if len(self.temp_points) == 2 and self.selected_objects:
                self.apply_transformation()

    def handle_drag(self, event):
        x, y = event.pos
        for i, obj in enumerate(self.selected_objects):
            offset_x, offset_y = self.drag_offset[i]
            obj.move((x - offset_x, y - offset_y))

    def handle_key_down(self, event):
        if event.key == pygame.K_RETURN and self.current_tool == "polygon":
            if len(self.temp_points) >= 3:
                self.objects.append(Polygon(self.temp_points, self.current_color))
                self.temp_points = []
                self.status = "Многоугольник создан"

        elif event.key == pygame.K_DELETE:
            for obj in self.selected_objects:
                if obj in self.objects:
                    self.objects.remove(obj)
            self.selected_objects = []
            self.status = "Объекты удалены"

        elif event.key == pygame.K_ESCAPE:
            self.temp_points = []
            self.status = "Операция отменена"

        elif event.key == pygame.K_u:
            self.current_tool = "union"
            self.apply_tmo_operation()

        elif event.key == pygame.K_d:
            self.current_tool = "sym_diff"
            self.apply_tmo_operation()

    def apply_transformation(self):
        center = self.temp_points[0]
        target = self.temp_points[1]

        for obj in self.selected_objects:
            if self.current_tool == "rotate":
                angle = Transformation.calculate_angle(center, target)
                obj.rotate(angle, center)
                self.status = f"Поворот на {int(angle)}°"

            elif self.current_tool == "scale_x":
                sx = Transformation.calculate_scale(center, target, 'x')
                obj.scale_x(sx, center)
                self.status = f"Масштаб по X: {sx:.1f}"

            elif self.current_tool == "scale_xy":
                scale = Transformation.calculate_scale(center, target, 'xy')
                obj.scale_xy(scale, center)
                self.status = f"Масштаб XY: {scale:.1f}"

        self.temp_points = []

    def apply_tmo_operation(self):
        if len(self.selected_objects) == 2:
            obj1, obj2 = self.selected_objects
            if self.current_tool == "union":
                result = TMOperations.union(obj1, obj2)
                if result:
                    self.objects.remove(obj1)
                    self.objects.remove(obj2)
                    self.objects.append(result)
                    self.selected_objects = [result]  # Выбираем новый объект
                    self.status = "Операция объединения выполнена"
                    print("Объединение выполнено:", result.points)  # Отладочное сообщение
                else:
                    self.status = "Не удалось выполнить объединение"
                    print("Объединение не удалось")  # Отладочное сообщение
            elif self.current_tool == "sym_diff":
                result = TMOperations.symmetric_difference(obj1, obj2)
                if result:
                    self.objects.remove(obj1)
                    self.objects.remove(obj2)
                    self.objects.append(result)
                    self.selected_objects = [result]  # Выбираем новый объект
                    self.status = "Симметрическая разность выполнена"
                    print("Симметрическая разность выполнена:", result.points)  # Отладочное сообщение
                else:
                    self.status = "Не удалось выполнить симметрическую разность"
                    print("Симметрическая разность не удалась")  # Отладочное сообщение
        else:
            self.status = "Выделите ровно 2 объекта для TMO"
            print("Необходимо выделить ровно 2 объекта")  # Отладочное сообщение

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_events()

            self.screen.fill(self.background)

            for x in range(0, self.width, 20):
                pygame.draw.line(self.screen, (220, 220, 220), (x, 0), (x, self.height))
            for y in range(0, self.height, 20):
                pygame.draw.line(self.screen, (220, 220, 220), (0, y), (self.width, y))

            for obj in self.objects:
                obj.draw(self.screen)
                if obj in self.selected_objects:
                    obj.draw_selection(self.screen)

            for point in self.temp_points:
                pygame.draw.circle(self.screen, (255, 0, 0), point, 5)

            self.toolbar.draw(self.screen)
            self.palette.draw(self.screen)

            status_surface = self.font.render(self.status, True, (0, 0, 0))
            self.screen.blit(status_surface, (10, self.height - 30))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
