# lgui/training_panel.py
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt # 导入Qt模块以使用对齐常量


class TrainingPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 标题标签
        title_label = QLabel("数据训练面板")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter) # 使用Qt.AlignCenter

        # 描述标签
        desc_label = QLabel("点击下方按钮启动数据收集器或训练模型。")
        desc_label.setAlignment(Qt.AlignCenter) # 使用Qt.AlignCenter

        # 按钮
        collect_btn = QPushButton("启动数据收集器")
        collect_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        collect_btn.clicked.connect(self.start_collector)

        train_static_btn = QPushButton("训练静态手势模型")
        train_static_btn.setStyleSheet("padding: 10px; font-size: 14px; background-color: #d4edda;")
        train_static_btn.clicked.connect(self.train_static_model)

        train_dynamic_btn = QPushButton("训练动态手势模型")
        train_dynamic_btn.setStyleSheet("padding: 10px; font-size: 14px; background-color: #fff3cd;")
        train_dynamic_btn.clicked.connect(self.train_dynamic_model)

        # 将控件添加到布局
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(collect_btn)
        layout.addWidget(train_static_btn)
        layout.addWidget(train_dynamic_btn)

        self.setLayout(layout)

    def start_collector(self):
        """启动独立的数据收集器GUI"""
        try:
            subprocess.Popen(["python", "DatasetCollector.py"])
            # PyQt5的消息框
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("启动成功")
            msg_box.setText("数据收集器已启动，请在新窗口中操作。")
            msg_box.exec_()
        except FileNotFoundError:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("找不到 'DatasetCollector.py' 文件，请检查文件是否存在。")
            msg_box.exec_()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"启动收集器时发生错误: {e}")
            msg_box.exec_()

    def train_static_model(self):
        """启动静态模型训练脚本"""
        try:
            process = subprocess.Popen(["python", "training/train_static_model_from_npy.py"])
            process.wait()
            if process.returncode == 0:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("训练完成")
                msg_box.setText("静态手势模型已成功训练并保存。")
                msg_box.exec_()
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setWindowTitle("训练失败")
                msg_box.setText("模型训练过程中出现错误，请查看控制台输出。")
                msg_box.exec_()
        except FileNotFoundError:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("找不到 'training/train_static_model_from_npy.py' 文件。")
            msg_box.exec_()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"启动训练时发生错误: {e}")
            msg_box.exec_()

    def train_dynamic_model(self):
        """启动动态模型训练脚本"""
        try:
            process = subprocess.Popen(["python", "training/train_dynamic_model_from_npy.py"])
            process.wait()
            if process.returncode == 0:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("训练完成")
                msg_box.setText("动态手势模型已成功训练并保存。")
                msg_box.exec_()
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setWindowTitle("训练失败")
                msg_box.setText("动态模型训练过程中出现错误，请查看控制台输出。")
                msg_box.exec_()
        except FileNotFoundError:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText("找不到 'training/train_dynamic_model_from_npy.py' 文件。")
            msg_box.exec_()
        except Exception as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"启动动态训练时发生错误: {e}")
            msg_box.exec_()