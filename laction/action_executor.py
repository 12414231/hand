'''
# laction/action_executor.py
import pyautogui
import time
import json
import os
import subprocess  # 用于执行系统命令

CONFIG_FILE = "config/gesture_mapping.json"


class ActionExecutor:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.last_action_time = {}
        self.cooldown = 0.5
        self.action_map = self.load_action_map()
        # --- 新增：用于鼠标移动 ---
        self.is_mouse_moving_mode = False
        self.smooth_factor = 0.2  # 鼠标平滑移动系数，0-1之间，越小越平滑
        self.last_mouse_x = None
        self.last_mouse_y = None

    def load_action_map(self):
        """从配置文件加载手势到动作的映射"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                internal_map = {}
                for gesture, action_name in config.items():
                    func = getattr(self, f"_do_{action_name}", None)
                    if func:
                        internal_map[gesture] = func
                    else:
                        print(f"警告: 配置文件中指定的动作 '{action_name}' 不存在，跳过映射 '{gesture}'。")
                return internal_map
        else:
            print(f"警告: 未找到配置文件 {CONFIG_FILE}，使用默认映射。")
            return {}

    def execute(self, gesture_name, coordinate=None):  # 接收一个可选的coordinate参数
        """根据手势名称执行相应动作"""
        if gesture_name in self.action_map:
            action_func = self.action_map[gesture_name]
            current_time = time.time()

            # --- 新增逻辑：处理带坐标的 mouse_move ---
            if gesture_name == "open_palm" and coordinate:
                self._handle_mouse_move(coordinate)
                return  # 处理完后直接返回，不执行通用冷却逻辑

            # --- 通用冷却逻辑 ---
            if current_time - self.last_action_time.get(gesture_name, 0) > self.cooldown:
                action_func()
                self.last_action_time[gesture_name] = current_time
                print(f"执行动作: {gesture_name} -> {action_func.__name__}")
            else:
                print(f"动作 {gesture_name} 冷却中...")
        else:
            print(f"未知手势: {gesture_name}，无对应动作。")

    def _handle_mouse_move(self, coord):
        """处理鼠标跟随移动逻辑"""
        screen_width, screen_height = pyautogui.size()
        x_norm, y_norm = coord  # coord是一个归一化的坐标 (0-1, 0-1)

        target_x = int(x_norm * screen_width)
        target_y = int(y_norm * screen_height)

        # 平滑移动，防止抖动
        if self.last_mouse_x is None:
            self.last_mouse_x, self.last_mouse_y = pyautogui.position()

        new_x = self.last_mouse_x + (target_x - self.last_mouse_x) * self.smooth_factor
        new_y = self.last_mouse_y + (target_y - self.last_mouse_y) * self.smooth_factor

        pyautogui.moveTo(new_x, new_y)
        self.last_mouse_x, self.last_mouse_y = new_x, new_y

    # --- 已有的基本动作 ---
    def _do_click(self):
        pyautogui.click()

    def _do_right_click(self):
        pyautogui.rightClick()

    def _do_double_click(self):
        pyautogui.doubleClick()

    def _do_move_right(self):
        pyautogui.moveRel(100, 0, duration=0.2)

    def _do_move_left(self):
        pyautogui.moveRel(-100, 0, duration=0.2)

    def _do_scroll_up(self):
        pyautogui.scroll(3)

    def _do_scroll_down(self):
        pyautogui.scroll(-3)

    def _do_drag(self):
        # 修正：使用相对坐标拖拽
        pyautogui.dragRel(200, 0, duration=1.0, button='left')

    # --- 新增/修改的高级动作 ---
    def _do_mouse_move(self):
        # 此功能由 _handle_mouse_move 在接收到坐标时处理
        pass

    def _do_volume_up(self):
        # Windows系统下的音量增加快捷键
        pyautogui.press('volumeup')

    def _do_volume_down(self):
        # Windows系统下的音量减少快捷键
        pyautogui.press('volumedown')

    def _do_screenshot(self):
        # 使用pyautogui截取全屏并保存
        screenshot = pyautogui.screenshot()
        screenshot.save(f"screenshot_{int(time.time())}.png")
        print("截图已保存。")

    def _do_back(self):
        # Windows下后退快捷键 (Alt + Left Arrow)
        pyautogui.keyDown('alt')
        pyautogui.press('left')
        pyautogui.keyUp('alt')

    def _do_forward(self):
        # Windows下前进快捷键 (Alt + Right Arrow)
        pyautogui.keyDown('alt')
        pyautogui.press('right')
        pyautogui.keyUp('alt')

    def _do_switch_window(self):
        # Windows下切换窗口快捷键 (Alt + Tab)
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')

    def _do_stop(self):
        # 什么都不做
        pass

    def _do_scroll_mode(self):
        # 标记进入滚动模式，可以在此处添加状态标志
        print("进入滚动模式，可以通过其他手势退出。")

    def reload_config(self):
        """重新加载配置文件"""
        self.action_map = self.load_action_map()
        print("动作配置已重新加载。")
'''
'''
# laction/action_executor.py
import pyautogui
import time
import json
import os
import subprocess  # 用于执行系统命令
from collections import deque

CONFIG_FILE = "config/gesture_mapping.json"


class ActionExecutor:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.last_action_time = {}
        self.cooldown = 0.5
        self.action_map = self.load_action_map()

        # --- 用于鼠标移动 ---
        self.is_mouse_moving_mode = False
        # 引入一个缓冲区来存储最近的几个坐标，用于平滑处理
        self.coord_buffer = deque(maxlen=5)
        self.last_smoothed_x = None
        self.last_smoothed_y = None
        self.mouse_move_last_executed = 0
        # 降低鼠标移动的执行频率，例如每0.05秒执行一次
        self.MOUSE_MOVE_INTERVAL = 0.05

    def load_action_map(self):
        """从配置文件加载手势到动作的映射"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                internal_map = {}
                for gesture, action_name in config.items():
                    func = getattr(self, f"_do_{action_name}", None)
                    if func:
                        internal_map[gesture] = func
                    else:
                        print(f"警告: 配置文件中指定的动作 '{action_name}' 不存在，跳过映射 '{gesture}'。")
                return internal_map
        else:
            print(f"警告: 未找到配置文件 {CONFIG_FILE}，使用默认映射。")
            return {}

    def execute(self, gesture_name, coordinate=None):  # 接收一个可选的coordinate参数
        """根据手势名称执行相应动作"""
        if gesture_name in self.action_map:
            action_func = self.action_map[gesture_name]
            current_time = time.time()

            # --- 重要修改：处理带坐标的 mouse_move ---
            if gesture_name == "open_palm" and coordinate:
                self._handle_mouse_move(coordinate)
                return  # 处理完后直接返回，不执行通用冷却逻辑

            # --- 通用冷却逻辑 ---
            if current_time - self.last_action_time.get(gesture_name, 0) > self.cooldown:
                action_func()
                self.last_action_time[gesture_name] = current_time
                print(f"执行动作: {gesture_name} -> {action_func.__name__}")
            else:
                print(f"动作 {gesture_name} 冷却中...")
        else:
            print(f"未知手势: {gesture_name}，无对应动作。")

    def _handle_mouse_move(self, coord):
        """处理鼠标跟随移动逻辑，增加缓冲区和平滑算法"""
        screen_width, screen_height = pyautogui.size()
        x_norm, y_norm = coord  # coord是一个归一化的坐标 (0-1, 0-1)

        target_x = int(x_norm * screen_width)
        target_y = int(y_norm * screen_height)

        # 将新的目标坐标加入缓冲区
        self.coord_buffer.append((target_x, target_y))

        # 计算缓冲区内坐标的加权平均值，最新的坐标权重更高
        total_weight = 0
        weighted_sum_x = 0
        weighted_sum_y = 0
        for i, (x, y) in enumerate(self.coord_buffer):
            weight = i + 1  # 索引越靠后，权重越大
            weighted_sum_x += x * weight
            weighted_sum_y += y * weight
            total_weight += weight

        smoothed_target_x = weighted_sum_x / total_weight
        smoothed_target_y = weighted_sum_y / total_weight

        current_time = time.time()
        # 控制鼠标移动的执行频率
        if current_time - self.mouse_move_last_executed < self.MOUSE_MOVE_INTERVAL:
            return

        # --- 改进的平滑移动算法 ---
        # 如果是第一次移动，则直接跳到目标位置
        if self.last_smoothed_x is None or self.last_smoothed_y is None:
            self.last_smoothed_x = smoothed_target_x
            self.last_smoothed_y = smoothed_target_y
            pyautogui.moveTo(self.last_smoothed_x, self.last_smoothed_y)
            self.mouse_move_last_executed = current_time
            return

        # 计算当前位置到平滑目标的距离
        dx = smoothed_target_x - self.last_smoothed_x
        dy = smoothed_target_y - self.last_smoothed_y

        # 定义一个“阻力”或“速度”，让移动看起来更自然
        # 距离越远，移动的比例越大
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 1:  # 如果距离非常小，则不再移动，防止微小抖动
            return

        # 速度系数，可以根据需要调整，数值越小越平滑
        speed_factor = 0.6

        move_dx = dx * speed_factor
        move_dy = dy * speed_factor

        new_x = self.last_smoothed_x + move_dx
        new_y = self.last_smoothed_y + move_dy

        pyautogui.moveTo(new_x, new_y)
        # 更新记录的最后位置
        self.last_smoothed_x, self.last_smoothed_y = new_x, new_y
        self.mouse_move_last_executed = current_time

    # --- 已有的基本动作 ---
    def _do_click(self):
        pyautogui.click()

    def _do_right_click(self):
        pyautogui.rightClick()

    def _do_double_click(self):
        pyautogui.doubleClick()

    def _do_move_right(self):
        pyautogui.moveRel(100, 0, duration=0.2)

    def _do_move_left(self):
        pyautogui.moveRel(-100, 0, duration=0.2)

    def _do_scroll_up(self):
        pyautogui.scroll(3)

    def _do_scroll_down(self):
        pyautogui.scroll(-3)

    def _do_drag(self):
        # 修正：使用相对坐标拖拽
        pyautogui.dragRel(200, 0, duration=1.0, button='left')

    # --- 新增/修改的高级动作 ---
    def _do_mouse_move(self):
        # 此功能由 _handle_mouse_move 在接收到坐标时处理
        pass

    def _do_volume_up(self):
        # Windows系统下的音量增加快捷键
        pyautogui.press('volumeup')

    def _do_volume_down(self):
        # Windows系统下的音量减少快捷键
        pyautogui.press('volumedown')

    def _do_screenshot(self):
        # 使用pyautogui截取全屏并保存
        screenshot = pyautogui.screenshot()
        screenshot.save(f"screenshot_{int(time.time())}.png")
        print("截图已保存。")

    def _do_back(self):
        # Windows下后退快捷键 (Alt + Left Arrow)
        pyautogui.keyDown('alt')
        pyautogui.press('left')
        pyautogui.keyUp('alt')

    def _do_forward(self):
        # Windows下前进快捷键 (Alt + Right Arrow)
        pyautogui.keyDown('alt')
        pyautogui.press('right')
        pyautogui.keyUp('alt')

    def _do_switch_window(self):
        # Windows下切换窗口快捷键 (Alt + Tab)
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')

    def _do_stop(self):
        # 什么都不做
        pass

    def _do_scroll_mode(self):
        # 标记进入滚动模式，可以在此处添加状态标志
        print("进入滚动模式，可以通过其他手势退出。")

    def reload_config(self):
        """重新加载配置文件"""
        self.action_map = self.load_action_map()
        print("动作配置已重新加载。")
'''
# laction/action_executor.py
import pyautogui
import time
import json
import os
import subprocess  # 用于执行系统命令
from collections import deque

CONFIG_FILE = "config/gesture_mapping.json"


class ActionExecutor:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.last_action_time = {}
        # --- 修改：使用字典为不同动作设置冷却时间 ---
        self.cooldown_times = {
            # 默认动作的冷却时间
            "default": 0.5,
            # 特定动作的冷却时间，例如 call_gesture 需要更快的响应
            "call_gesture": 0.1,
            # 也可以为其他动作单独设置，例如点击可能需要更长的冷却
            # "click": 0.2,
        }
        self.action_map = self.load_action_map()

        # --- 用于鼠标移动 ---
        self.is_mouse_moving_mode = False
        # 引入一个缓冲区来存储最近的几个坐标，用于平滑处理
        self.coord_buffer = deque(maxlen=5)
        self.last_smoothed_x = None
        self.last_smoothed_y = None
        self.mouse_move_last_executed = 0
        # 降低鼠标移动的执行频率，例如每0.05秒执行一次
        self.MOUSE_MOVE_INTERVAL = 0.05

        # --- 用于处理手势冲突 ---
        self._last_gesture_for_conflict = None

    def load_action_map(self):
        """从配置文件加载手势到动作的映射"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                internal_map = {}
                for gesture, action_name in config.items():
                    func = getattr(self, f"_do_{action_name}", None)
                    if func:
                        internal_map[gesture] = func
                    else:
                        print(f"警告: 配置文件中指定的动作 '{action_name}' 不存在，跳过映射 '{gesture}'。")
                return internal_map
        else:
            print(f"警告: 未找到配置文件 {CONFIG_FILE}，使用默认映射。")
            return {}

    def execute(self, gesture_name, coordinate=None):  # 接收一个可选的coordinate参数
        """根据手势名称执行相应动作"""

        # --- 处理 open_palm 和 pinch 的冲突 ---
        if self.is_mouse_moving_mode and gesture_name == "pinch":
            print(f"[ActionExecutor] 忽略冲突手势: {gesture_name} (因正处于鼠标移动模式)")
            return

        # 更新状态：如果当前是 open_palm，激活鼠标移动模式；否则关闭
        if gesture_name == "open_palm":
            if not self.is_mouse_moving_mode:
                self.is_mouse_moving_mode = True
                self.coord_buffer.clear()
                self.last_smoothed_x = None
                self.last_smoothed_y = None
                print("[ActionExecutor] 进入鼠标移动模式")
        else:
            if self.is_mouse_moving_mode:
                self.is_mouse_moving_mode = False
                print("[ActionExecutor] 退出鼠标移动模式")

        if gesture_name in self.action_map:
            action_func = self.action_map[gesture_name]
            current_time = time.time()

            # --- 处理带坐标的 mouse_move ---
            if gesture_name == "open_palm" and coordinate:
                self._handle_mouse_move(coordinate)
                return  # 处理完后直接返回，不执行通用冷却逻辑

            # --- 修改后的通用冷却逻辑 ---
            # 获取该动作的特定冷却时间，如果没有定义则使用默认值
            cooldown_time = self.cooldown_times.get(gesture_name, self.cooldown_times["default"])

            if current_time - self.last_action_time.get(gesture_name, 0) > cooldown_time:
                action_func()
                self.last_action_time[gesture_name] = current_time
                print(f"执行动作: {gesture_name} -> {action_func.__name__}")
            else:
                print(f"动作 {gesture_name} 冷却中...")
        else:
            print(f"未知手势: {gesture_name}，无对应动作。")

    def _handle_mouse_move(self, coord):
        """处理鼠标跟随移动逻辑，增加缓冲区和平滑算法"""
        screen_width, screen_height = pyautogui.size()
        x_norm, y_norm = coord  # coord是一个归一化的坐标 (0-1, 0-1)

        target_x = int(x_norm * screen_width)
        target_y = int(y_norm * screen_height)

        # 将新的目标坐标加入缓冲区
        self.coord_buffer.append((target_x, target_y))

        # 计算缓冲区内坐标的加权平均值，最新的坐标权重更高
        total_weight = 0
        weighted_sum_x = 0
        weighted_sum_y = 0
        for i, (x, y) in enumerate(self.coord_buffer):
            weight = i + 1  # 索引越靠后，权重越大
            weighted_sum_x += x * weight
            weighted_sum_y += y * weight
            total_weight += weight

        smoothed_target_x = weighted_sum_x / total_weight
        smoothed_target_y = weighted_sum_y / total_weight

        current_time = time.time()
        # 控制鼠标移动的执行频率
        if current_time - self.mouse_move_last_executed < self.MOUSE_MOVE_INTERVAL:
            return

        # --- 改进的平滑移动算法 ---
        if self.last_smoothed_x is None or self.last_smoothed_y is None:
            self.last_smoothed_x = smoothed_target_x
            self.last_smoothed_y = smoothed_target_y
            pyautogui.moveTo(self.last_smoothed_x, self.last_smoothed_y)
            self.mouse_move_last_executed = current_time
            return

        dx = smoothed_target_x - self.last_smoothed_x
        dy = smoothed_target_y - self.last_smoothed_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 1:
            return

        speed_factor = 0.6
        move_dx = dx * speed_factor
        move_dy = dy * speed_factor

        new_x = self.last_smoothed_x + move_dx
        new_y = self.last_smoothed_y + move_dy

        pyautogui.moveTo(new_x, new_y)
        self.last_smoothed_x, self.last_smoothed_y = new_x, new_y
        self.mouse_move_last_executed = current_time

    # --- 已有的基本动作 ---
    def _do_click(self):
        pyautogui.click()

    def _do_right_click(self):
        pyautogui.rightClick()

    def _do_double_click(self):
        pyautogui.doubleClick()

    def _do_move_right(self):
        pyautogui.moveRel(400, 0, duration=0.2)

    def _do_move_left(self):
        pyautogui.moveRel(-400, 0, duration=0.2)

    def _do_scroll_up(self):
        pyautogui.scroll(100)

    def _do_scroll_down(self):
        pyautogui.scroll(-100)

    def _do_drag(self):
        pyautogui.dragRel(200, 0, duration=1.0, button='left')

    # --- 新增/修改的高级动作 ---
    def _do_mouse_move(self):
        pass

    def _do_volume_up(self):
        pyautogui.press('volumeup')

    def _do_volume_down(self):
        pyautogui.press('volumedown')

    def _do_screenshot(self):
        """
        直接使用PIL/Pillow进行截图，绕过键盘快捷键，避免冲突。
        """
        from PIL import ImageGrab
        import datetime

        try:
            screenshot = ImageGrab.grab()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            screenshot.save(filename)
            print(f"截图已保存至: {filename}")
        except Exception as e:
            print(f"截图失败: {e}")

    def _do_back(self):
        pyautogui.keyDown('alt')
        pyautogui.press('left')
        pyautogui.keyUp('alt')

    def _do_forward(self):
        pyautogui.keyDown('alt')
        pyautogui.press('right')
        pyautogui.keyUp('alt')

    def _do_switch_window(self):
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')

    def _do_stop(self):
        pass

    def _do_scroll_mode(self):
        print("进入滚动模式，可以通过其他手势退出。")

    def reload_config(self):
        """重新加载配置文件"""
        self.action_map = self.load_action_map()
        print("动作配置已重新加载。")