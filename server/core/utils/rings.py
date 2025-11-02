from locale import normalize
import math


class Ring:
    def __init__(self, n: int):
        """
            Тут использую кольцо так как координаты это в целом два кольца
            R/Rn
        """
        self.n = n

    def to_geographical(self, value: float):
        """
        Интерполирует [0] -> [+] в [-] -> [+]
        """
        if value > self.n or value < 0:
            raise ValueError("Value is out of range")

        return value - self.n // 2

    def to_flat(self, value: float):
        """
        Интерполирует [-] -> [+] в [0] -> [+]
        """
        if abs(value) > self.n // 2:
            raise ValueError("Value is out of range")

        return self.normalise(value + self.n // 2)

    def normalise(self, value: float):
        """
        Нормализует значение на кольце
        value % n
        """
        if value < 0:
            value = abs(value) % self.n
            return (self.n - value) % self.n

        return value % self.n

    # Опреации
    def add(self, a, b):
        return self.normalise(a + b)

    def sub(self, a, b):
        return self.normalise(a - b)

    def mul(self, a, b):
        return self.normalise(a * b)

    def div(self, a, b):
        return self.normalise(a / b)

    def pow(self, a, b):
        return self.normalise(a ** b)

    def sqrt(self, a):
        return self.normalise(a ** 0.5)

    def log(self, a, b):
        return self.normalise(math.log(a, b))

    def exp(self, a):
        return self.normalise(math.exp(a))

    # Методы

    def in_between(self, a, c, b):
        """
            Проверяет находится ли c между a и b
        """
        if a > b:
            # Сдвигаем все по a
            b = self.sub(b, a)
            c = self.sub(c, a)
            a = 0
            # print("Change", a, c, b)

        return a <= c <= b

class EarthRing:
    def __init__(self):
        self.lat = Ring(180)
        self.lon = Ring(360)

    def in_frame(self, a, c, b):
        x1,y1 = a
        x2,y2 = b
        x3,y3 = c

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # print(x1, x3, x2)
        # print(y1, y3, y2)

        # print(self.lon.in_between(x1, x3, x2), self.lat.in_between(y1, y3, y2))

        return self.lon.in_between(x1, x3, x2) and self.lat.in_between(y1, y3, y2)

    def in_circle(self, a, r, center):
        x, y = a
        cx, cy = center
        R = 6371000
        rrad = r / R * 180 / math.pi
        return (x - cx) ** 2 + (y - cy) ** 2 <= rrad ** 2

    def to_flat(self, point: tuple[float, float]):
        return self.lon.to_flat(point[0]), self.lat.to_flat(point[1])

    def to_geographical(self, point: tuple[float, float]):
        return self.lon.to_geographical(point[0]), self.lat.to_geographical(point[1])

    def normalise(self, point: tuple[float, float]):
        return self.lon.normalise(point[0]), self.lat.normalise(point[1])


# earth = EarthRing()
# a = (45.1939588,5.6556953)
# c = (45.1637322,5.7861847)
# b = (45.1437322,5.7761573)

# a = earth.to_flat(a)
# b = earth.to_flat(b)
# c = earth.to_flat(c)


# print(earth.in_frame(a, c, b))


