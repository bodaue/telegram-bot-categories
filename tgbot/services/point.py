class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def in_polygon(self, cords):
        xp, yp = self.__change_cords(cords)
        c = 0
        for i in range(len(xp)):
            if ((yp[i] <= self.y < yp[i - 1] or (yp[i - 1] <= self.y < yp[i])) and
                    (self.x > (xp[i - 1] - xp[i]) * (self.y - yp[i]) / (yp[i - 1] - yp[i]) + xp[i])):
                c = 1 - c
        return c

    @staticmethod
    def __change_cords(cords: list[list[int | float]]):
        x_cords = []
        y_cords = []

        for point in cords:
            x = point[0]
            y = point[1]
            x_cords.append(x)
            y_cords.append(y)
        return x_cords, y_cords

    def __str__(self):
        return f'{self.x}, {self.y}'
