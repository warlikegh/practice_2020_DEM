from Line import *
from Coordinate import *

# Класс Wall по-хорошему надо сделать Singleton`ом, но я не знаю как это реализуется в Python,
# поэтому пока запихнул в конструктор Ball
#
# Класс Wall принимает в себя координаты, но пока они бесполезны(как возможно и в будущем)
#
# Для некоего синтаксического сахара необходимы:
#   - проверка на связность линий
#   - проверка на выпуклость многоугольника
#   - соотвествующие исключения
#   - конструктор, принимающий на вход только координаты(и строящий на их основе массив линий)
#   - конструктор, принимающий на вход только линии
#
# Класс Wall может принимать в себя любое количество линий и координат


class Wall:
    def __init__(self, canvas, color, coordinates=None, lines=None):
        if coordinates is None:
            coordinates = [Coordinate(), Coordinate()]
        if lines is None:
            lines = []
            for i in range(len(coordinates)):
                lines.append(Line(coordinates[i % len(coordinates)], coordinates[(i + 1) % len(coordinates)]))

        self.coordinates = coordinates
        self.lines = lines
        for line in self.lines:
            canvas.create_line(line.x1, line.y1, line.x2, line.y2, fill=color)
