import numpy as np
from collections import deque


class KalmanFilter1D:
    """一个简单的一维卡尔曼滤波器，可用于平滑关键点坐标"""

    def __init__(self, process_noise=1e-5, measurement_noise=1e-2, error_estimate=1):
        self.q = process_noise  # 过程噪声
        self.r = measurement_noise  # 测量噪声
        self.p = error_estimate  # 误差协方差
        self.x = 0  # 状态估计

    def update(self, measurement):
        # 预测
        p_new = self.p + self.q

        # 更新
        k = p_new / (p_new + self.r)  # 卡尔曼增益
        self.x = self.x + k * (measurement - self.x)
        self.p = (1 - k) * p_new

        return self.x


class MovingAverageFilter:
    """移动平均滤波器"""

    def __init__(self, window_size=5):
        self.window = deque(maxlen=window_size)

    def update(self, value):
        self.window.append(value)
        return sum(self.window) / len(self.window)