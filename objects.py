class Barrier:
    def __init__(self):
        self.size_x = 41
        self.size_y = 1

        self.x, self.y = 686, 0

    def set_y(self, y):
        self.y = y

    def set_size_y(self, value):
        self.size_y = value

    def get_y(self):
        return self.y

    def get_size(self):
        return (self.size_x, self.size_y)


class Mirror:
    pass
