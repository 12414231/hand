
from .static_recognition import predict_static
from .dynamic_recognition import predict_dynamic
from  utilsss.trajectory_buffer import TrajectoryBuffer

class GestureEngine:

    def __init__(self):

        self.buffer=TrajectoryBuffer()

    def process(self,features,index_x,index_y):

        static,prob=predict_static(features)

        self.buffer.add(index_x,index_y)

        seq=self.buffer.get()

        dynamic=None

        if seq is not None:

            dynamic=predict_dynamic(seq)

            self.buffer.reset()

        return static,prob,dynamic
