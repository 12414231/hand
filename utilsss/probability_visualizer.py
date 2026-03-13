import cv2
import numpy as np


class ProbabilityVisualizer:
    def __init__(self, class_names, position=(10, 200), bar_height=20, max_bar_width=200):
        self.class_names = class_names
        self.position = position
        self.bar_height = bar_height
        self.max_bar_width = max_bar_width

    def draw(self, image, probabilities):
        """
        在图像上绘制概率条形图。
        :param image: OpenCV 图像
        :param probabilities: 一个包含每个类别概率的列表或数组
        """
        start_x, start_y = self.position
        for i, (class_name, prob) in enumerate(zip(self.class_names, probabilities)):
            # 计算条形图宽度
            bar_width = int((prob / 1.0) * self.max_bar_width)

            # 定义条形图的顶点
            top_left = (start_x, start_y + i * (self.bar_height + 5))
            bottom_right = (start_x + bar_width, start_y + (i + 1) * (self.bar_height + 5) - 5)

            # 绘制背景矩形（灰色）
            cv2.rectangle(image, top_left, bottom_right, (50, 50, 50), thickness=cv2.FILLED)

            # 绘制前景概率矩形（蓝色）
            cv2.rectangle(image, top_left, bottom_right, (255, 100, 0), thickness=cv2.FILLED)

            # 添加类别名称和概率文本
            text = f"{class_name}: {prob:.2f}"
            text_position = (bottom_right[0] + 10, bottom_right[1] - 5)
            cv2.putText(image, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return image