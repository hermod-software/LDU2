class Bounds: # a class to more easily handle bounding boxes and things we need from them
    def __init__(self, bounds):
        self.bounds = bounds
        self.left = bounds[0]
        self.top = bounds[1]
        self.right = bounds[2]
        self.bottom = bounds[3]
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        self.hmiddle = round(self.left + self.width / 2) # can't be a float
        self.vmiddle = round(self.top + self.height / 2) # can't be a float
        self.centre = (self.hmiddle, self.vmiddle)

        self.topleft = (self.left, self.top)
        self.topright = (self.right, self.top)
        self.bottomleft = (self.left, self.bottom)
        self.bottomright = (self.right, self.bottom)