'''
# lgui/camera_widget.py
import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


class CameraWidget(QWidget):
    def __init__(self, gesture_engine):
        super().__init__()
        self.gesture_engine = gesture_engine
        self.cap = cv2.VideoCapture(0)

        # 默认模式
        self.current_mode = "static"

        self.init_ui()
        self.start_camera()

    def init_ui(self):
        layout = QVBoxLayout()

        # 模式选择下拉框
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["静态模型模式", "动态模型模式"])  # 修改选项文字
        self.mode_selector.currentTextChanged.connect(self.on_mode_changed)
        self.mode_selector.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 14px;
            }
        """)

        # 视频显示标签
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)

        # 识别结果标签
        self.result_label = QLabel("识别结果: ")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; color: blue;")

        layout.addWidget(self.mode_selector)
        layout.addWidget(self.video_label)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def on_mode_changed(self, text):
        """当下拉框选项改变时触发"""
        if text == "静态模型模式":
            self.current_mode = "static"
        elif text == "动态模型模式":
            self.current_mode = "dynamic"
        print(f"切换到: {text} (internal: {self.current_mode})")

    def start_camera(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # 将当前模式告知GestureEngine
        self.gesture_engine.set_current_mode(self.current_mode)

        # 使用GestureEngine处理帧
        annotated_frame, current_gesture = self.gesture_engine.process_frame(frame)

        # 更新GUI显示
        h, w, ch = annotated_frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(annotated_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

        self.result_label.setText(f"识别结果: {current_gesture}")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        event.accept()
'''



'''
# lgui/camera_widget.py
import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


class CameraWidget(QWidget):
    def __init__(self, gesture_engine):
        super().__init__()
        self.gesture_engine = gesture_engine
        self.cap = cv2.VideoCapture(0)

        # 默认模式
        self.current_mode = "static"

        self.init_ui()
        self.start_camera()

    def init_ui(self):
        layout = QVBoxLayout()

        # 模式选择下拉框
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["静态模型模式", "动态模型模式"])  # 修改选项文字
        self.mode_selector.currentTextChanged.connect(self.on_mode_changed)
        self.mode_selector.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 14px;
            }
        """)

        # 视频显示标签
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)

        # 识别结果标签
        self.result_label = QLabel("识别结果: ")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; color: blue;")

        layout.addWidget(self.mode_selector)
        layout.addWidget(self.video_label)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def on_mode_changed(self, text):
        """当下拉框选项改变时触发"""
        if text == "静态模型模式":
            self.current_mode = "static"
        elif text == "动态模型模式":
            self.current_mode = "dynamic"
        print(f"切换到: {text} (internal: {self.current_mode})")

    def start_camera(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # --- 镜像翻转 ---
        # 在处理前对帧进行水平翻转
        frame = cv2.flip(frame, 1)

        # 将当前模式告知GestureEngine
        self.gesture_engine.set_current_mode(self.current_mode)

        # 使用GestureEngine处理帧
        annotated_frame, current_gesture = self.gesture_engine.process_frame(frame)

        # 更新GUI显示
        h, w, ch = annotated_frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(annotated_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

        self.result_label.setText(f"识别结果: {current_gesture}")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        event.accept()'''
# lgui/camera_widget.py
# lgui/camera_widget.py
import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


class CameraWidget(QWidget):
    def __init__(self, gesture_engine):
        super().__init__()
        self.gesture_engine = gesture_engine
        self.cap = cv2.VideoCapture(0)

        # 内部跟踪当前模式，用于比对变化
        self.current_mode = "static"
        # 标记是否是首次初始化，避免首次设置触发信号
        self._initializing = True

        self.init_ui()
        self._initializing = False  # 初始化完成后取消标记
        self.start_camera()

    def init_ui(self):
        layout = QVBoxLayout()

        # 模式选择下拉框
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["静态模型模式", "动态模型模式"])
        # 设置初始索引，这会触发信号，但我们用 _initializing 标记来忽略它
        self.mode_selector.setCurrentIndex(0 if self.current_mode == "static" else 1)
        self.mode_selector.currentTextChanged.connect(self.on_mode_changed)
        self.mode_selector.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-size: 14px;
            }
        """)

        # 视频显示标签
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)

        # 识别结果标签
        self.result_label = QLabel("识别结果: ")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; color: blue;")

        layout.addWidget(self.mode_selector)
        layout.addWidget(self.video_label)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def on_mode_changed(self, text):
        """当下拉框选项改变时触发"""
        # 如果是初始化期间，则忽略信号
        if self._initializing:
            return

        # 根据UI上的文字确定内部模式
        if text == "静态模型模式":
            new_mode = "static"
        elif text == "动态模型模式":
            new_mode = "dynamic"
        else:
            return  # 无效选项，忽略

        # 只有在模式真正发生变化时才更新
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            print(f"UI触发模式切换: {text} (internal: {self.current_mode})")
            # 通知手势引擎切换模式
            self.gesture_engine.set_current_mode(self.current_mode)

    def start_camera(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # --- 镜像翻转 ---
        frame = cv2.flip(frame, 1)

        # 将当前模式告知GestureEngine
        # 注意：这里不再重复调用 set_current_mode，
        # 因为模式切换应该由UI事件驱动，而不是每一帧都驱动。
        # self.gesture_engine.set_current_mode(self.current_mode) # 移除这一行

        # 使用GestureEngine处理帧
        annotated_frame, current_gesture = self.gesture_engine.process_frame(frame)

        # --- 新增：如果正在追踪动态手势，在画面上添加提示 ---
        if self.gesture_engine.is_tracking_dynamic:
            cv2.putText(annotated_frame, "DYNAMIC GESTURE TRACKING...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 更新GUI显示
        h, w, ch = annotated_frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(annotated_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

        self.result_label.setText(f"识别结果: {current_gesture}")

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        event.accept()