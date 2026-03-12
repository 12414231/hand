import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk

from linference.gesture_engine import GestureEngine
from utilsss.feature_extractor import extract_landmarks

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


class CameraWidget:

    def __init__(self, root, label):

        self.root = root
        self.label = label

        self.cap = cv2.VideoCapture(0)

        self.engine = GestureEngine()

        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        self.running = True

    def update(self):

        if not self.running:
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.hands.process(rgb)

        gesture_text = ""

        if result.multi_hand_landmarks:

            for hand in result.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    hand,
                    mp_hands.HAND_CONNECTIONS
                )

                # 提取特征
                features = extract_landmarks(hand)

                index_x = hand.landmark[8].x
                index_y = hand.landmark[8].y

                static, prob, dynamic = self.engine.process(
                    features,
                    index_x,
                    index_y
                )

                gesture_text = f"{static} ({prob:.2f})"

        # 显示手势文字
        cv2.putText(
            frame,
            gesture_text,
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # 转为Tk图像
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(img)

        imgtk = ImageTk.PhotoImage(image=img)

        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

        self.root.after(10, self.update)

    def stop(self):

        self.running = False
        self.cap.release()