# lgui/mapping_panel.py
import json
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem
)

MAPPING_FILE = "config/gesture_mapping.json"


class MappingPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.mappings = self.load_mappings()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title_label = QLabel("手势映射配置")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # 添加映射的输入框和按钮
        input_layout = QHBoxLayout()
        self.gesture_input = QLineEdit()
        self.gesture_input.setPlaceholderText("输入手势名称 (例如: click)")
        self.action_input = QLineEdit()
        self.action_input.setPlaceholderText("输入动作 (例如: click, move_right, scroll_up)")

        add_btn = QPushButton("添加映射")
        add_btn.clicked.connect(self.add_mapping)

        input_layout.addWidget(self.gesture_input)
        input_layout.addWidget(self.action_input)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        # 显示现有映射的列表
        self.mapping_list = QListWidget()
        self.refresh_list()
        layout.addWidget(self.mapping_list)

        # 删除选中项按钮
        delete_btn = QPushButton("删除选中")
        delete_btn.clicked.connect(self.delete_selected)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def load_mappings(self):
        """从JSON文件加载映射关系"""
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "click": "click",
                "move_right": "move_right",
                "move_left": "move_left",
                "scroll_up": "scroll_up",
                "scroll_down": "scroll_down"
            }

    def save_mappings(self):
        """将映射关系保存到JSON文件"""
        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.mappings, f, ensure_ascii=False, indent=4)

    def refresh_list(self):
        """刷新列表视图"""
        self.mapping_list.clear()
        for gesture, action in self.mappings.items():
            item_text = f"{gesture} -> {action}"
            item = QListWidgetItem(item_text)
            item.setData(32, (gesture, action))
            self.mapping_list.addItem(item)

    def add_mapping(self):
        """添加新的映射关系"""
        gesture = self.gesture_input.text().strip()
        action = self.action_input.text().strip()

        if gesture and action:
            self.mappings[gesture] = action
            self.save_mappings()
            self.refresh_list()
            self.gesture_input.clear()
            self.action_input.clear()
            print(f"添加映射: {gesture} -> {action}")

    def delete_selected(self):
        """删除列表中选中的项"""
        selected_items = self.mapping_list.selectedItems()
        for item in selected_items:
            gesture, _ = item.data(32)
            if gesture in self.mappings:
                del self.mappings[gesture]

        self.save_mappings()
        self.refresh_list()
        print(f"删除了 {len(selected_items)} 个映射项。")