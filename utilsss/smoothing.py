class MouseSmoother:

    def __init__(self,factor):

        self.factor=factor
        self.prev_x=0
        self.prev_y=0

    def smooth(self,x,y):

        sx=int((self.prev_x*(self.factor-1)+x)/self.factor)
        sy=int((self.prev_y*(self.factor-1)+y)/self.factor)

        self.prev_x=sx
        self.prev_y=sy

        return sx,sy