from collections import deque


class TrajectoryBuffer:
    def __init__(self, max_length=16):
        self.buffer = deque(maxlen=max_length)

    def add(self, landmarks):
        """添加一个新的关键点帧到缓冲区"""
        self.buffer.append(landmarks)

    def get_trajectory(self):
        """获取完整的轨迹"""
        return list(self.buffer)

    def is_full(self):
        """检查缓冲区是否已满"""
        return len(self.buffer) == self.buffer.maxlen

    def clear(self):
        """清空缓冲区"""
        self.buffer.clear()

    def size(self):
        """获取当前缓冲区大小"""
        return len(self.buffer)