# lgui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from lgui.camera_widget import CameraWidget
from lgui.mapping_panel import MappingPanel
from lgui.training_panel import TrainingPanel

class MainWindow(QMainWindow):
    def __init__(self, gesture_engine):
        super().__init__()
        self.setWindowTitle("手势识别与映射系统")
        self.setGeometry(100, 100, 1000, 700)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 创建各个面板
        self.camera_tab = CameraWidget(gesture_engine)
        self.mapping_tab = MappingPanel()
        self.training_tab = TrainingPanel()

        # 添加到主窗口
        self.tab_widget.addTab(self.camera_tab, "手势识别")
        self.tab_widget.addTab(self.mapping_tab, "按键映射")
        self.tab_widget.addTab(self.training_tab, "数据训练")

        # 不再需要组件间通信，因为ActionExecutor总是启用的，
        # 模式切换由CameraWidget直接控制GestureEngine