import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import numpy as np
import time
import os
from PIL import Image, ImageTk

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "dataset", "static")
DYNAMIC_DIR = os.path.join(BASE_DIR, "dataset", "dynamic")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(DYNAMIC_DIR, exist_ok=True)


class DatasetCollector:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Gesture Dataset Collector")
        self.root.geometry("950x720")

        self.cap = cv2.VideoCapture(0)

        self.interval = 0.15
        self.last_time = 0

        self.collecting = False

        # 动态序列
        self.sequence = []
        self.seq_len = 30

        # 静态手势
        self.static_gestures = [
            "open_palm","fist","thumb_up","thumb_down",
            "pinch","two_fingers","three_fingers",
            "four_fingers","split_fingers","call_gesture"
        ]

        # 动态手势
        self.dynamic_gestures = [
            "circle","line_left","line_right",
            "up_line","down_line","Z"
        ]

        self.data = []

        self.create_ui()
        self.update_stats()
        self.update_camera()

        self.root.mainloop()

    # GUI

    def create_ui(self):

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        panel = tk.Frame(self.root)
        panel.pack(pady=10)

        tk.Label(panel,text="Mode").grid(row=0,column=0)

        self.mode_var = tk.StringVar(value="static")

        tk.Radiobutton(panel,text="Static",
                       variable=self.mode_var,value="static",
                       command=self.update_gesture_list).grid(row=0,column=1)

        tk.Radiobutton(panel,text="Dynamic",
                       variable=self.mode_var,value="dynamic",
                       command=self.update_gesture_list).grid(row=0,column=2)

        tk.Label(panel,text="Gesture").grid(row=1,column=0)

        self.gesture_var = tk.StringVar()

        self.gesture_box = ttk.Combobox(panel,textvariable=self.gesture_var,width=20)
        self.gesture_box.grid(row=1,column=1)

        self.update_gesture_list()

        self.sample_label = tk.Label(panel,text="Current Samples: 0")
        self.sample_label.grid(row=2,column=0)

        self.status_label = tk.Label(panel,text="Status: Idle")
        self.status_label.grid(row=2,column=1)

        tk.Button(panel,text="Start",command=self.start).grid(row=3,column=0)
        tk.Button(panel,text="Stop",command=self.stop).grid(row=3,column=1)

        self.stats_box = tk.Text(self.root,height=14,width=50)
        self.stats_box.pack()

    # 更新手势列表

    def update_gesture_list(self):

        mode = self.mode_var.get()

        if mode == "static":
            gestures = self.static_gestures
        else:
            gestures = self.dynamic_gestures

        self.gesture_box["values"] = gestures
        self.gesture_box.current(0)

    # 摄像头

    def update_camera(self):

        ret,frame = self.cap.read()

        if not ret:
            return

        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        result = hands.process(rgb)

        if result.multi_hand_landmarks:

            hand = result.multi_hand_landmarks[0]

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            if self.collecting:

                if self.mode_var.get() == "static":
                    self.collect_static(hand)

                else:
                    self.collect_dynamic(hand)

        gesture = self.gesture_var.get()

        cv2.putText(frame,f"Gesture: {gesture}",(20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        img = Image.fromarray(frame)

        imgtk = ImageTk.PhotoImage(image=img)

        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(10,self.update_camera)

    # 静态采集

    def collect_static(self,hand):

        if time.time()-self.last_time < self.interval:
            return

        landmarks=[]

        for lm in hand.landmark:
            landmarks.extend([lm.x,lm.y,lm.z])

        self.data.append(landmarks)

        self.sample_label.config(text=f"Current Samples: {len(self.data)}")

        self.last_time=time.time()

    # 动态采集

    def collect_dynamic(self,hand):

        index = hand.landmark[8]

        self.sequence.append([index.x,index.y])

        if len(self.sequence)==self.seq_len:

            self.data.append(self.sequence)

            self.sequence=[]

            self.sample_label.config(text=f"Current Samples: {len(self.data)}")

    # 控制

    def start(self):

        self.collecting=True
        self.data=[]
        self.sequence=[]

        self.status_label.config(text="Status: Collecting")

    def stop(self):

        self.collecting=False

        self.status_label.config(text="Saving...")

        self.save()

        self.update_stats()

        self.status_label.config(text="Idle")

    # 保存

    def save(self):

        gesture=self.gesture_var.get()

        if self.mode_var.get()=="static":
            path=os.path.join(STATIC_DIR,f"{gesture}.npy")
        else:
            path=os.path.join(DYNAMIC_DIR,f"{gesture}.npy")

        if os.path.exists(path):

            old=np.load(path,allow_pickle=True)

            new=np.concatenate([old,np.array(self.data)])

        else:

            new=np.array(self.data)

        np.save(path,new)

        print("Saved",gesture,len(new))

    # 统计

    def update_stats(self):

        self.stats_box.delete(1.0,tk.END)

        self.stats_box.insert(tk.END,"STATIC\n\n")

        for g in self.static_gestures:

            path=os.path.join(STATIC_DIR,f"{g}.npy")

            if os.path.exists(path):
                count=len(np.load(path,allow_pickle=True))
            else:
                count=0

            self.stats_box.insert(tk.END,f"{g:<15} {count}\n")

        self.stats_box.insert(tk.END,"\nDYNAMIC\n\n")

        for g in self.dynamic_gestures:

            path=os.path.join(DYNAMIC_DIR,f"{g}.npy")

            if os.path.exists(path):
                count=len(np.load(path,allow_pickle=True))
            else:
                count=0

            self.stats_box.insert(tk.END,f"{g:<15} {count}\n")


if __name__=="__main__":
    DatasetCollector()