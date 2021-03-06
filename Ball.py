from MoveWall import *


# Для синтаксического сахара необходимо в конструкторе проверять на принадлежность стенке


class Ball:
    def __init__(self, x, y, radius, alpha, velocity, cn, cs, density, color, canvas):
        self.x = x
        self.y = y
        self.theta = 0
        self.mass = density * pi * radius ** 2
        # Коэффициент контактного демпфирования в нормальном направлении
        self.cn = cn
        # Коэффициент контактного демпфирования в тангенциальном направлении
        self.cs = cs
        self.radius = radius
        self.accelerationX = accelerationX
        self.accelerationY = accelerationY
        self.velocityAbsolute = velocity
        self.alphaRadian = alpha * pi / 180
        self.velocityX = velocity * cos(self.alphaRadian)
        self.velocityY = velocity * sin(self.alphaRadian)
        self.velocityTheta = 0
        self.canvas = canvas
        self.id = canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)
        self.id2 = canvas.create_line(x, y, x + radius * cos(self.theta), y + radius * sin(self.theta), width=2,
                                      fill="black")
        self.isCrossAnything = False

    def drawPolygon(self):
        self.movePolygon()  # фактическое движение
        self.canvas.move(self.id, self.velocityX * deltaTime, self.velocityY * deltaTime)  # прорисовка движения

    def rotationIndicator(self):
        self.theta += (self.velocityTheta * deltaTime) % (2 * pi)
        self.canvas.coords(self.id2, self.x, self.y, self.x + self.radius * cos(self.theta),
                           self.y + self.radius * sin(self.theta))
        self.canvas.move(self.id2, self.velocityX * deltaTime, self.velocityY * deltaTime)

    def movePolygon(self):
        pos = self.canvas.coords(self.id)  # овал задается по 4-м коордиатам по которым
        self.x = (pos[0] + pos[2]) / 2  # можно найти координаты центра
        self.y = (pos[1] + pos[3]) / 2

        # Смена направления происходит в двух случаях(для обоих разные последствия):
        #   - Пересечения мячом линии стенки
        #   - Выхода за границы стенки(скорость больше радиуса * 2)
        if self.crossPolygon():
            self.resetPolygon()
        elif not self.isInsidePolygon():
            self.comeBack()
        # Обновление направлений скоростей
        self.velocityX = self.velocityAbsolute * cos(self.alphaRadian) + self.accelerationX * deltaTime
        self.velocityY = self.velocityAbsolute * sin(self.alphaRadian) + self.accelerationY * deltaTime
        self.changeVelocity(atan2(self.velocityY, self.velocityX + eps),
                            sqrt((self.velocityX ** 2) + (self.velocityY ** 2)))

    def crossPolygon(self):
        # Проверяет пересечение как минимум с одной линией
        for line in MoveWall.getInstance().lines:
            if line.crossLine(self.x, self.y, self.radius):
                return True
        return False

    def resetPolygon(self):
        # Находим линию, которую пересекает шарик и изменяем угол шарика по известной формуле:
        # alpha = 2 * beta - alpha
        wall = MoveWall.getInstance()
        for line in wall.lines:
            if line.crossLine(self.x, self.y, self.radius):
                # Проверка на то двигается ли мячик к линии или от нее
                # (во втором случае менять направление не нужно)
                if self.resetForLine(line):
                    self.alphaRadian = 2 * line.alphaTau - self.alphaRadian
                    alphaRadianLocal = self.alphaRadian - line.alphaNorm
                    velocityXLocal = self.velocityAbsolute * cos(alphaRadianLocal)
                    velocityYLocal = self.velocityAbsolute * sin(alphaRadianLocal)
                    if wall.flagMove:
                        velocityXLocalWall = wall.velocityAbsolute * cos(alphaRadianLocal)
                        velocityYLocalWall = wall.velocityAbsolute * sin(alphaRadianLocal)
                    else:
                        velocityXLocalWall = 0
                        velocityYLocalWall = 0
                    velocityXLocal += velocityXLocalWall
                    dampeningNormal = velocityXLocal * cn_wall
                    dampeningTangent = (velocityYLocal - velocityYLocalWall) * cs_wall
                    self.velocityTheta += 1 / self.radius * (1 - cs_wall) * (
                            velocityYLocal - velocityYLocalWall - (self.velocityTheta * self.radius)) * (
                                   deltaTime ** 2)
                    velocityXLocalNew = dampeningVelocity(dampeningNormal, velocityXLocal)
                    velocityYLocalNew = dampeningVelocity(dampeningTangent, velocityYLocal)
                    self.changeVelocity(atan2(velocityYLocalNew, velocityXLocalNew + eps) + line.alphaNorm,
                                        sqrt(velocityXLocalNew ** 2 + velocityYLocalNew ** 2))

    def resetForLine(self, line):
        # Проверяем расстояние сейчас и в следующий момент времени
        # (с учетом нахождения внутри стен)
        # Если сейчас расстояние больше - мячик двигается к стенке
        distNow = line.distanceToLine(self.x, self.y)
        if not self.isInsidePolygon():
            distNow *= -1

        self.x += self.velocityX * deltaTime
        self.y += self.velocityY * deltaTime
        distAfter = line.distanceToLine(self.x, self.y)
        if not self.isInsidePolygon():
            distAfter *= -1
        self.x -= self.velocityX * deltaTime
        self.y -= self.velocityY * deltaTime

        return distNow > distAfter

    def isInsidePolygon(self):
        # Направляем луч из центра шарика вертикально вверх и считаем количество пересечений с линиями стенки
        # Если количество пересечений кратно двум, значит мяч вышел за границу стенки
        summary = 0
        for line in MoveWall.getInstance().lines:
            if line.crossVerticalUp(self.x, self.y):
                summary += 1
        if summary % 2 == 1:
            return True
        else:
            return False

    def comeBack(self):
        # Возвращаем мяч в стенки в случае его выброса:
        # Находим линию к которой мячу будет логичнее всего стремиться
        # (меньше всего расстояние и перпендекуляр попадает в линию(в отрезок линии))
        # и меняем направление в соответсвии с этой линией
        distances = []
        for line in MoveWall.getInstance().lines:
            distances.append(line.distanceToLine(self.x, self.y))
        minDistance = min(distances)
        key = True

        while key:
            for line in MoveWall.getInstance().lines:
                if abs(line.distanceToLine(self.x, self.y) - minDistance) < eps:
                    h = line.distanceToLine(self.x, self.y)
                    xH = self.x + h * cos(pi - line.alphaNorm)
                    yH = self.y - h * sin(pi - line.alphaNorm)
                    if line.isLine(xH, yH) or len(distances) == 1:
                        key = False
                    else:
                        distances.remove(minDistance)
                        minDistance = min(distances)

        for line in MoveWall.getInstance().lines:
            if abs(line.distanceToLine(self.x, self.y) - minDistance) < eps:
                self.alphaRadian = 2 * line.alphaTau - self.alphaRadian
                return

    def changeVelocity(self, newAlpha, newVelocityAbsolute):
        # Изменение вектора скорости
        self.alphaRadian = newAlpha
        self.velocityAbsolute = newVelocityAbsolute
        self.velocityX = newVelocityAbsolute * cos(newAlpha)
        self.velocityY = newVelocityAbsolute * sin(newAlpha)

    def getAlpha(self):
        return self.alphaRadian * 180 / pi

    def getAcceleration(self):
        return self.velocityAbsolute / deltaTime

    def setAcceleration(self):
        if self.isCrossAnything:
            self.removeAcceleration()
        else:
            self.addAcceleration()

    def removeAcceleration(self):
        self.accelerationX = 0
        self.accelerationY = 0

    def addAcceleration(self):
        self.accelerationX = MoveWall.getInstance().accelerationX
        self.accelerationY = MoveWall.getInstance().accelerationY
