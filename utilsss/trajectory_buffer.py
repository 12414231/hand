import numpy as np

class TrajectoryBuffer:

    def __init__(self,max_len=30):

        self.max_len=max_len
        self.points=[]

    def add(self,x,y):

        self.points.append([x,y])

        if len(self.points)>self.max_len:
            self.points.pop(0)

    def get(self):

        if len(self.points)<self.max_len:
            return None

        return np.array(self.points)

    def reset(self):

        self.points=[]