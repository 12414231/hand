from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget
from lgui.training_panel import TrainingPanel
from lgui.mapping_panel import MappingPanel


class ControlPanel(QWidget):
    def __init__(self, gesture_engine):
        super().__init__()
        self.engine = gesture_engine
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Gesture AI OS Pro - 控制中心')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        title_label = QLabel("Gesture AI OS Pro")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title_label)

        # 创建一个标签页控件来组织不同的面板
        tab_widget = QTabWidget()

        # 添加训练面板
        self.training_panel = TrainingPanel(self.engine)
        tab_widget.addTab(self.training_panel, "训练数据")

        # 添加映射面板
        self.mapping_panel = MappingPanel()
        tab_widget.addTab(self.mapping_panel, "手势映射")

        # 添加一个日志或信息显示区域
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMaximumHeight(150)
        tab_widget.addTab(self.info_display, "系统信息")

        layout.addWidget(tab_widget)

        # 底部按钮布局
        button_layout = QHBoxLayout()

        btn_train_static = QPushButton("训练静态模型")
        btn_train_static.clicked.connect(self.on_train_static_clicked)
        button_layout.addWidget(btn_train_static)

        btn_train_dynamic = QPushButton("训练动态模型")
        btn_train_dynamic.clicked.connect(self.on_train_dynamic_clicked)
        button_layout.addWidget(btn_train_dynamic)

        btn_exit = QPushButton("退出")
        btn_exit.clicked.connect(self.close)
        button_layout.addWidget(btn_exit)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_train_static_clicked(self):
        # 这里可以触发一个线程来执行训练，避免阻塞UI
        import subprocess
        subprocess.Popen(["python", "training/train_static_model.py"])
        self.info_display.append("启动静态模型训练...")

    def on_train_dynamic_clicked(self):
        import subprocess
        subprocess.Popen(["python", "training/train_lstm_model.py"])
        self.info_display.append("启动动态模型训练...")