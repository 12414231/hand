# DatasetCollector.py
import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import numpy as np
import time
import os
from PIL import Image, ImageTk

# --- 初始化 Mediapipe ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

# --- 路径设置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "datasets", "static")
DYNAMIC_DIR = os.path.join(BASE_DIR, "datasets", "dynamic")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(DYNAMIC_DIR, exist_ok=True)


class DatasetCollector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gesture Dataset Collector - Auto Mode")
        self.root.geometry("950x720")

        self.cap = cv2.VideoCapture(0)

        # 自动收集的时间间隔（秒）
        self.collection_interval = 0.15
        self.last_collection_time = 0

        # 动态序列相关（暂未启用）
        self.sequence = []
        self.seq_len = 30

        # 手势列表
        self.static_gestures = [
            "open_palm", "fist", "thumb_up", "thumb_down",
            "pinch", "two_fingers", "three_fingers",
            "four_fingers", "split_fingers", "call_gesture"
        ]
        self.dynamic_gestures = [
            "circle", "line_left", "line_right",
            "up_line", "down_line", "Z"
        ]

        # 当前目标手势
        self.target_gesture = ""
        # 当前模式
        self.current_mode = "static"

        self.create_ui()
        self.update_stats()
        self.update_camera()

    def run(self):
        """启动GUI主循环"""
        self.root.mainloop()

    def create_ui(self):
        # 视频显示区域
        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # 控制面板
        panel = tk.Frame(self.root)
        panel.pack(pady=10)

        # 模式选择
        tk.Label(panel, text="Mode:").grid(row=0, column=0, sticky='e')
        self.mode_var = tk.StringVar(value="static")
        tk.Radiobutton(panel, text="Static", variable=self.mode_var, value="static", command=self.on_mode_change).grid(
            row=0, column=1)
        tk.Radiobutton(panel, text="Dynamic", variable=self.mode_var, value="dynamic",
                       command=self.on_mode_change).grid(row=0, column=2)

        # 手势选择
        tk.Label(panel, text="Target Gesture:").grid(row=1, column=0, sticky='e')
        self.gesture_var = tk.StringVar()
        self.gesture_box = ttk.Combobox(panel, textvariable=self.gesture_var, width=20, state="readonly")
        self.gesture_box.grid(row=1, column=1, columnspan=2)
        # 绑定选择事件，实现切换手势
        self.gesture_box.bind("<<ComboboxSelected>>", self.on_gesture_selected)

        # 初始化下拉框内容
        self.update_gesture_list()

        # 状态和统计信息
        self.status_label = tk.Label(panel, text="Status: Monitoring (Select a gesture to start collecting)")
        self.status_label.grid(row=2, column=0, columnspan=3)

        # 样本数量统计
        self.sample_count_label = tk.Label(panel, text="Current Gesture Samples: 0")
        self.sample_count_label.grid(row=3, column=0, columnspan=3)

        # 统计文本框
        self.stats_box = tk.Text(self.root, height=14, width=50)
        self.stats_box.pack()

    def on_mode_change(self):
        """当模式改变时，更新下拉框列表"""
        self.update_gesture_list()
        self.target_gesture = ""  # 清空当前目标手势
        self.update_status()

    def update_gesture_list(self):
        """根据当前模式更新下拉框选项"""
        mode = self.mode_var.get()
        if mode == "static":
            gestures = self.static_gestures
        else:
            gestures = self.dynamic_gestures

        self.gesture_box['values'] = gestures
        self.gesture_box.set('')  # 清空当前选择

    def on_gesture_selected(self, event):
        """当下拉框选中一个手势时，更新目标手势"""
        self.target_gesture = self.gesture_var.get()
        self.update_status()
        # 更新当前手势的样本数量
        self.update_current_gesture_sample_count()

    def update_current_gesture_sample_count(self):
        """更新当前选中手势的已存在样本数"""
        if not self.target_gesture:
            self.sample_count_label.config(text="Current Gesture Samples: 0")
            return

        mode = self.mode_var.get()
        if mode == "static":
            path = os.path.join(STATIC_DIR, f"{self.target_gesture}.npy")
        else:
            path = os.path.join(DYNAMIC_DIR, f"{self.target_gesture}.npy")

        if os.path.exists(path):
            data = np.load(path, allow_pickle=True)
            count = len(data)
        else:
            count = 0

        self.sample_count_label.config(text=f"Current Gesture Samples: {count}")

    def update_status(self):
        """更新状态栏文本"""
        if self.target_gesture:
            self.status_label.config(
                text=f"Status: Collecting '{self.target_gesture}' data automatically when hand is detected.")
        else:
            self.status_label.config(text="Status: Monitoring (Select a gesture to start collecting)")

    def update_camera(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        collecting_this_frame = False
        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            # --- 核心逻辑：自动收集 ---
            if self.target_gesture and time.time() - self.last_collection_time > self.collection_interval:
                if self.current_mode == "static":
                    self.collect_static(hand)
                # elif self.current_mode == "dynamic": # 动态逻辑待实现
                #     self.collect_dynamic(hand)
                self.last_collection_time = time.time()
                collecting_this_frame = True

        # 显示目标手势和收集状态
        status_text = f"Target: {self.target_gesture or 'None'}"
        if collecting_this_frame:
            status_text += " | [COLLECTING]"
        cv2.putText(frame, status_text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 将OpenCV图像转换为PIL格式并更新到GUI
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_camera)

    def collect_static(self, hand):
        """收集静态手势数据"""
        if not self.target_gesture:
            return

        landmarks = []
        for lm in hand.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])

        # 实时保存，追加到.npy文件
        self.save_sample_to_npy(self.target_gesture, np.array(landmarks), "static")

    def collect_dynamic(self, hand):
        """收集动态手势数据（预留接口，逻辑待完善）"""
        # index_tip = hand.landmark[8]
        # self.sequence.append([index_tip.x, index_tip.y])
        # if len(self.sequence) == self.seq_len:
        #     self.save_sample_to_npy(self.target_gesture, np.array(self.sequence), "dynamic")
        #     self.sequence = []
        pass  # 此功能需进一步开发

    def save_sample_to_npy(self, gesture_name, new_sample, mode):
        """将单个样本追加保存到对应的.npy文件"""
        if mode == "static":
            path = os.path.join(STATIC_DIR, f"{gesture_name}.npy")
        else:
            path = os.path.join(DYNAMIC_DIR, f"{gesture_name}.npy")

        if os.path.exists(path):
            # 加载现有数据
            old_data = np.load(path, allow_pickle=True)
            # 追加新样本
            new_data = np.append(old_data, [new_sample], axis=0)
        else:
            # 如果文件不存在，创建新数组
            new_data = np.array([new_sample])

        # 保存回文件
        np.save(path, new_data)
        print(f"Saved sample for '{gesture_name}'. Total samples: {len(new_data)}")

        # 更新GUI上的统计信息
        self.update_current_gesture_sample_count()
        # 更新全局统计
        self.update_stats()

    def update_stats(self):
        """更新右侧的全局统计信息"""
        self.stats_box.delete(1.0, tk.END)
        self.stats_box.insert(tk.END, "STATIC GESTURES\n" + "=" * 20 + "\n")

        for g in self.static_gestures:
            path = os.path.join(STATIC_DIR, f"{g}.npy")
            if os.path.exists(path):
                count = len(np.load(path, allow_pickle=True))
            else:
                count = 0
            self.stats_box.insert(tk.END, f"{g:<20} : {count}\n")

        self.stats_box.insert(tk.END, "\nDYNAMIC GESTURES\n" + "=" * 20 + "\n")

        for g in self.dynamic_gestures:
            path = os.path.join(DYNAMIC_DIR, f"{g}.npy")
            if os.path.exists(path):
                count = len(np.load(path, allow_pickle=True))
            else:
                count = 0
            self.stats_box.insert(tk.END, f"{g:<20} : {count}\n")


# 如果直接运行此脚本，则启动收集器
if __name__ == "__main__":
    collector = DatasetCollector()
    collector.run()