'''
# linference/gesture_engine.py
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque


class GestureEngine:
    def __init__(self, static_predictor=None, dynamic_predictor=None, action_executor=None):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils

        self.static_predictor = static_predictor
        self.dynamic_predictor = dynamic_predictor
        self.action_executor = action_executor

        # --- 用于动态手势识别 ---
        self.index_tip_history = deque(maxlen=30)
        self.dynamic_gesture_threshold = 0.05
        self.is_tracking_dynamic = False
        self.tracking_start_time = None
        self.TRACKING_DURATION = 2.0

        # --- 当前模式 ---
        self.current_mode = "static"

    def set_current_mode(self, mode):
        if mode in ["static", "dynamic"]:
            self.current_mode = mode
            print(f"GestureEngine模式已切换为: {mode}")
            self.is_tracking_dynamic = False
            self.index_tip_history.clear()

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        current_gesture = "None"
        annotated_frame = frame.copy()

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )

            # 计算手掌中心点作为坐标参考
            palm_center = self._calculate_palm_center(hand_landmarks, w, h)

            if self.current_mode == "dynamic" and self.dynamic_predictor:
                # --- 动态手势识别逻辑 ---
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                current_pos = (index_tip.x, index_tip.y)

                if not self.is_tracking_dynamic:
                    if len(self.index_tip_history) > 1:
                        last_pos = self.index_tip_history[-1]
                        distance_moved = np.sqrt(
                            (current_pos[0] - last_pos[0]) ** 2 + (current_pos[1] - last_pos[1]) ** 2)

                        if distance_moved > self.dynamic_gesture_threshold:
                            self.is_tracking_dynamic = True
                            self.tracking_start_time = time.time()
                            self.index_tip_history.clear()
                            print("开始追踪动态手势...")

                if self.is_tracking_dynamic:
                    self.index_tip_history.append(current_pos)

                    if time.time() - self.tracking_start_time >= self.TRACKING_DURATION:
                        if len(self.index_tip_history) > 5:
                            trajectory = list(self.index_tip_history)
                            current_gesture = self._predict_dynamic(trajectory)
                            # --- 执行动作 (动态手势通常不需要坐标) ---
                            if self.action_executor:
                                self.action_executor.execute(current_gesture)
                        else:
                            current_gesture = "None"

                        self.is_tracking_dynamic = False
                        self.index_tip_history.clear()
                        print("动态手势追踪结束。")

            elif self.current_mode == "static" and self.static_predictor:
                # --- 静态手势识别逻辑 ---
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])

                current_gesture = self._predict_static(landmarks)
                # --- 执行动作 (带上坐标) ---
                if self.action_executor:
                    # 只有 open_palm 需要坐标，其他手势传 None
                    coordinate_to_pass = palm_center if current_gesture == "open_palm" else None
                    self.action_executor.execute(current_gesture, coordinate_to_pass)

        return annotated_frame, current_gesture

    def _predict_static(self, landmarks):
        if self.static_predictor:
            return self.static_predictor.predict(landmarks)
        return "Model Not Loaded"

    def _predict_dynamic(self, trajectory):
        if self.dynamic_predictor:
            return self.dynamic_predictor.predict(trajectory)
        return "Dynamic Model Not Loaded"

    def _calculate_palm_center(self, hand_landmarks, image_width, image_height):
        """计算手掌中心点的归一化坐标 (0-1, 0-1)"""
        # 选取几个关键点来估算手掌中心
        # 这里选用手腕(Wrist), 中指根部(MCP), 和食指根部(MCP)
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        middle_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        index_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]

        # 计算这些点的平均值作为中心
        center_x = (wrist.x + middle_mcp.x + index_mcp.x) / 3.0
        center_y = (wrist.y + middle_mcp.y + index_mcp.y) / 3.0

        # 归一化坐标 (0-1, 0-1)
        return (center_x, center_y)

    def release(self):
        self.hands.close()'''



'''
# linference/gesture_engine.py
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque


class GestureEngine:
    def __init__(self, static_predictor=None, dynamic_predictor=None, action_executor=None):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils

        self.static_predictor = static_predictor
        self.dynamic_predictor = dynamic_predictor
        self.action_executor = action_executor

        # --- 用于动态手势识别 ---
        self.index_tip_history = deque(maxlen=30)
        self.dynamic_gesture_threshold = 0.05
        self.is_tracking_dynamic = False
        self.tracking_start_time = None
        self.TRACKING_DURATION = 2.0

        # --- 当前模式 ---
        self.current_mode = "static"

    def set_current_mode(self, mode):
        if mode in ["static", "dynamic"]:
            self.current_mode = mode
            print(f"GestureEngine模式已切换为: {mode}")
            self.is_tracking_dynamic = False
            self.index_tip_history.clear()

    def process_frame(self, frame):
        h, w, _ = frame.shape
        # --- 重要：翻转整个帧以匹配摄像头预览 ---
        frame_flipped = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        current_gesture = "None"
        annotated_frame = frame_flipped.copy()  # 使用翻转后的帧

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )

            # 计算手掌中心点作为坐标参考
            palm_center = self._calculate_palm_center(hand_landmarks, w, h)

            # --- 修复镜像：翻转X坐标 (左右翻转) ---
            palm_center_x, palm_center_y = palm_center
            flipped_palm_center = (1 - palm_center_x, palm_center_y)

            if self.current_mode == "dynamic" and self.dynamic_predictor:
                # --- 动态手势识别逻辑 ---
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                current_pos = (index_tip.x, index_tip.y)

                if not self.is_tracking_dynamic:
                    if len(self.index_tip_history) > 1:
                        last_pos = self.index_tip_history[-1]
                        distance_moved = np.sqrt(
                            (current_pos[0] - last_pos[0]) ** 2 + (current_pos[1] - last_pos[1]) ** 2)

                        if distance_moved > self.dynamic_gesture_threshold:
                            self.is_tracking_dynamic = True
                            self.tracking_start_time = time.time()
                            self.index_tip_history.clear()
                            print("开始追踪动态手势...")

                if self.is_tracking_dynamic:
                    self.index_tip_history.append(current_pos)

                    if time.time() - self.tracking_start_time >= self.TRACKING_DURATION:
                        if len(self.index_tip_history) > 5:
                            trajectory = list(self.index_tip_history)
                            current_gesture = self._predict_dynamic(trajectory)
                            # --- 执行动作 (动态手势通常不需要坐标) ---
                            if self.action_executor:
                                self.action_executor.execute(current_gesture)
                        else:
                            current_gesture = "None"

                        self.is_tracking_dynamic = False
                        self.index_tip_history.clear()
                        print("动态手势追踪结束。")

            elif self.current_mode == "static" and self.static_predictor:
                # --- 静态手势识别逻辑 ---
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])

                current_gesture = self._predict_static(landmarks)
                # --- 执行动作 (带上坐标) ---
                if self.action_executor:
                    # 只有 open_palm 需要坐标，其他手势传 None
                    # 使用翻转后的坐标
                    coordinate_to_pass = flipped_palm_center if current_gesture == "open_palm" else None
                    self.action_executor.execute(current_gesture, coordinate_to_pass)

        return annotated_frame, current_gesture

    def _predict_static(self, landmarks):
        if self.static_predictor:
            return self.static_predictor.predict(landmarks)
        return "Model Not Loaded"

    def _predict_dynamic(self, trajectory):
        if self.dynamic_predictor:
            return self.dynamic_predictor.predict(trajectory)
        return "Dynamic Model Not Loaded"

    def _calculate_palm_center(self, hand_landmarks, image_width, image_height):
        """计算手掌中心点的归一化坐标 (0-1, 0-1)"""
        # 选取几个关键点来估算手掌中心
        # 这里选用手腕(Wrist), 中指根部(MCP), 和食指根部(MCP)
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        middle_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        index_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]

        # 计算这些点的平均值作为中心
        center_x = (wrist.x + middle_mcp.x + index_mcp.x) / 3.0
        center_y = (wrist.y + middle_mcp.y + index_mcp.y) / 3.0

        # 归一化坐标 (0-1, 0-1)
        return (center_x, center_y)

    def release(self):
        self.hands.close()'''
# linference/gesture_engine.py
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

'''
class GestureEngine:
    def __init__(self, static_predictor=None, dynamic_predictor=None, action_executor=None):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils

        self.static_predictor = static_predictor
        self.dynamic_predictor = dynamic_predictor
        self.action_executor = action_executor

        # --- 用于动态手势识别 ---
        self.index_tip_history = deque(maxlen=30)
        # 设置一个极低的阈值，或者干脆不使用阈值
        # self.dynamic_gesture_threshold = 0.02 # 注释掉旧的阈值
        self.is_tracking_dynamic = False
        self.tracking_start_time = None
        self.TRACKING_DURATION = 1.0

        # --- 当前模式 ---
        self.current_mode = "static"

    def set_current_mode(self, mode):
        if mode in ["static", "dynamic"]:
            self.current_mode = mode
            print(f"GestureEngine模式已切换为: {mode}")
            # 清空所有状态，确保干净的切换
            self.is_tracking_dynamic = False
            self.index_tip_history.clear()
            self.tracking_start_time = None

    def process_frame(self, frame):
        h, w, _ = frame.shape
        # --- 重要：翻转整个帧以匹配摄像头预览 ---
        frame_flipped = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        current_gesture = "None"
        annotated_frame = frame_flipped.copy()

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )

            # 计算手掌中心点作为坐标参考
            palm_center = self._calculate_palm_center(hand_landmarks, w, h)
            palm_center_x, palm_center_y = palm_center
            flipped_palm_center = (1 - palm_center_x, palm_center_y)

            if self.current_mode == "dynamic" and self.dynamic_predictor:
                # --- 动态手势识别逻辑 ---
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                current_pos = (index_tip.x, index_tip.y)

                # --- 修改：在动态模式下，只要检测到手，就开始追踪 ---
                if not self.is_tracking_dynamic:
                    self.is_tracking_dynamic = True
                    self.tracking_start_time = time.time()
                    # 清空历史，只保留当前点作为轨迹起点
                    self.index_tip_history.clear()
                    self.index_tip_history.append(current_pos)
                    print(f"[动态识别] 在动态模式下检测到手，开始追踪轨迹...")

                if self.is_tracking_dynamic:
                    # 如果正在追踪，持续记录指尖位置
                    self.index_tip_history.append(current_pos)

                    elapsed_time = time.time() - self.tracking_start_time
                    print(f"[动态识别] 追踪中... 已耗时: {elapsed_time:.2f}s, 轨迹点数: {len(self.index_tip_history)}")

                    # 检查是否到达设定的追踪时长
                    if elapsed_time >= self.TRACKING_DURATION:
                        if len(self.index_tip_history) > 5:  # 确保有足够的点来构成一个手势
                            trajectory = list(self.index_tip_history)
                            print(f"[动态识别] 轨迹收集完成，共 {len(trajectory)} 个点，准备预测...")

                            # 调用动态模型进行预测
                            predicted_gesture = self._predict_dynamic(trajectory)
                            print(f"[动态识别] 预测结果: {predicted_gesture}")

                            current_gesture = predicted_gesture

                            # --- 执行动作 ---
                            if self.action_executor:
                                self.action_executor.execute(current_gesture, coordinate=None)
                        else:
                            print(f"[动态识别] 结束追踪，但轨迹点不足 ({len(self.index_tip_history)} < 5)，忽略。")
                            current_gesture = "None"

                        # 无论成功与否，都重置追踪状态
                        self.is_tracking_dynamic = False
                        self.index_tip_history.clear()
                        self.tracking_start_time = None
                        print("[动态识别] 追踪结束，等待下一次手势。")

            elif self.current_mode == "static" and self.static_predictor:
                # --- 静态手势识别逻辑 ---
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])

                current_gesture = self._predict_static(landmarks)

                if self.action_executor:
                    coordinate_to_pass = flipped_palm_center if current_gesture == "open_palm" else None
                    self.action_executor.execute(current_gesture, coordinate_to_pass)

        else:
            # 如果没有检测到手，也应重置追踪状态
            if self.is_tracking_dynamic:
                print("[动态识别] 手脱离视野，强制结束追踪。")
                self.is_tracking_dynamic = False
                self.index_tip_history.clear()
                self.tracking_start_time = None

        return annotated_frame, current_gesture

    def _predict_static(self, landmarks):
        if self.static_predictor:
            return self.static_predictor.predict(landmarks)
        return "Static Model Not Loaded"

    def _predict_dynamic(self, trajectory):
        if self.dynamic_predictor:
            try:
                trajectory_np = np.array(trajectory)
                return self.dynamic_predictor.predict(trajectory_np)
            except Exception as e:
                print(f"[动态识别] 模型预测出错: {e}")
                return "Prediction Error"
        else:
            print("[动态识别] 动态模型未加载")
            return "Dynamic Model Not Loaded"

    def _calculate_palm_center(self, hand_landmarks, image_width, image_height):
        """计算手掌中心点的归一化坐标 (0-1, 0-1)"""
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        middle_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        index_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]

        center_x = (wrist.x + middle_mcp.x + index_mcp.x) / 3.0
        center_y = (wrist.y + middle_mcp.y + index_mcp.y) / 3.0

        return (center_x, center_y)

    def release(self):
        self.hands.close()# linference/gesture_engine.py'''
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque


class GestureEngine:
    def __init__(self, static_predictor=None, dynamic_predictor=None, action_executor=None):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils

        self.static_predictor = static_predictor
        self.dynamic_predictor = dynamic_predictor
        self.action_executor = action_executor

        # --- 用于动态手势识别 ---
        self.index_tip_history = deque(maxlen=30)
        self.is_tracking_dynamic = False
        self.tracking_start_time = None
        self.TRACKING_DURATION = 1.0

        # --- 当前模式 ---
        self.current_mode = "static"

    def set_current_mode(self, mode):
        if mode in ["static", "dynamic"]:
            self.current_mode = mode
            print(f"GestureEngine模式已切换为: {mode}")
            # 切换模式时，重置动态追踪状态
            self.is_tracking_dynamic = False
            self.index_tip_history.clear()
            self.tracking_start_time = None

    def process_frame(self, frame):
        h, w, _ = frame.shape
        # --- 重要：翻转整个帧以匹配摄像头预览 ---
        frame_flipped = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        current_gesture = "None"
        annotated_frame = frame_flipped.copy()

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )

            # 计算手掌中心点作为坐标参考
            palm_center = self._calculate_palm_center(hand_landmarks, w, h)
            palm_center_x, palm_center_y = palm_center
            flipped_palm_center = (1 - palm_center_x, palm_center_y)

            if self.current_mode == "dynamic" and self.dynamic_predictor:
                # --- 动态手势识别逻辑 ---
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                current_pos = (index_tip.x, index_tip.y)

                # --- 核心逻辑 ---
                # 如果没有在追踪，就启动追踪
                if not self.is_tracking_dynamic:
                    self.is_tracking_dynamic = True
                    self.tracking_start_time = time.time()
                    self.index_tip_history.clear() # 确保开始时历史是干净的
                    self.index_tip_history.append(current_pos)
                    print(f"[动态识别] 启动追踪，初始轨迹点数: {len(self.index_tip_history)}")

                # 如果已经在追踪，就添加新点并检查时间
                elif self.is_tracking_dynamic:
                    self.index_tip_history.append(current_pos) # 添加新点
                    elapsed_time = time.time() - self.tracking_start_time

                    # 打印详细信息以便调试
                    print(f"[动态识别] 追踪中... 已耗时: {elapsed_time:.2f}s, 当前帧添加后轨迹点数: {len(self.index_tip_history)}")

                    # 检查是否到达设定的追踪时长
                    if elapsed_time >= self.TRACKING_DURATION:
                        if len(self.index_tip_history) > 5:
                            trajectory = list(self.index_tip_history)
                            print(f"[动态识别] 轨迹收集完成，共 {len(trajectory)} 个点，准备预测...")

                            # 调用动态模型进行预测
                            predicted_gesture = self._predict_dynamic(trajectory)
                            print(f"[动态识别] 预测结果: {predicted_gesture}")

                            current_gesture = predicted_gesture

                            # --- 执行动作 ---
                            if self.action_executor:
                                self.action_executor.execute(current_gesture, coordinate=None)
                        else:
                            print(f"[动态识别] 结束追踪，但轨迹点不足 ({len(self.index_tip_history)} < 5)，忽略。")
                            current_gesture = "None"

                        # 无论成功与否，都重置追踪状态
                        self.is_tracking_dynamic = False
                        self.index_tip_history.clear()
                        self.tracking_start_time = None
                        print("[动态识别] 追踪结束，等待下一次手势。")

            elif self.current_mode == "static" and self.static_predictor:
                # --- 静态手势识别逻辑 ---
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])

                current_gesture = self._predict_static(landmarks)

                if self.action_executor:
                    coordinate_to_pass = flipped_palm_center if current_gesture == "open_palm" else None
                    self.action_executor.execute(current_gesture, coordinate_to_pass)

        else:
            # 如果没有检测到手，也应重置追踪状态
            if self.is_tracking_dynamic:
                print("[动态识别] 手脱离视野，强制结束追踪。")
                self.is_tracking_dynamic = False
                self.index_tip_history.clear()
                self.tracking_start_time = None

        return annotated_frame, current_gesture

    def _predict_static(self, landmarks):
        if self.static_predictor:
            return self.static_predictor.predict(landmarks)
        return "Static Model Not Loaded"

    def _predict_dynamic(self, trajectory):
        if self.dynamic_predictor:
            try:
                trajectory_np = np.array(trajectory)
                return self.dynamic_predictor.predict(trajectory_np)
            except Exception as e:
                print(f"[动态识别] 模型预测出错: {e}")
                return "Prediction Error"
        else:
            print("[动态识别] 动态模型未加载")
            return "Dynamic Model Not Loaded"

    def _calculate_palm_center(self, hand_landmarks, image_width, image_height):
        """计算手掌中心点的归一化坐标 (0-1, 0-1)"""
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        middle_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        index_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]

        center_x = (wrist.x + middle_mcp.x + index_mcp.x) / 3.0
        center_y = (wrist.y + middle_mcp.y + index_mcp.y) / 3.0

        return (center_x, center_y)

    def release(self):
        self.hands.close()