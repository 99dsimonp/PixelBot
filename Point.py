
# Point represents a point determined by x, y coordinates, such as screen pixel points or character coordinate points
class Point:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toString(self):
        return str(self.x) + ',' + str(self.y)
