import pyautogui
import pynput
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Listener, KeyCode
import time

pyautogui.FAILSAFE = False  # 防止鼠标移动到角落时程序中断
mouse = Controller()

class GestureActions:
    def __init__(self):
        self.scroll_mode_active = False
        self.scroll_accumulator = 0
        self.scroll_sensitivity = 0.5
        self.dragging = False
        self.mouse_hold_start_pos = None

    def execute_static_action(self, gesture_name):
        """执行静态手势对应的动作"""
        action_map = {
            "open_palm": self._action_mouse_move,
            "fist": self._action_left_click,
            "thumb_up": self._action_volume_up,
            "thumb_down": self._action_volume_down,
            "pinch": self._action_drag_toggle,
            "two_fingers": self._action_right_click,
            "three_fingers": self._action_double_click,
            "four_fingers": self._action_scroll_mode_toggle,
            "split_fingers": self._action_stop,
            "call_gesture": self._action_screenshot,
        }
        action_func = action_map.get(gesture_name)
        if action_func:
            action_func()

    def execute_dynamic_action(self, gesture_name):
        """执行动态手势对应的动作"""
        action_map = {
            "circle": self._action_screenshot,
            "line_left": self._action_back,
            "line_right": self._action_forward,
            "up_line": self._action_volume_up,
            "down_line": self._action_volume_down,
            "Z": self._action_switch_window,
        }
        action_func = action_map.get(gesture_name)
        if action_func:
            action_func()

    # --- 静态手势动作 ---
    def _action_mouse_move(self):
        pass  # 仅用于切换到移动模式，实际移动由GUI处理

    def _action_left_click(self):
        mouse.click(Button.left)

    def _action_right_click(self):
        mouse.click(Button.right)

    def _action_double_click(self):
        mouse.click(Button.left, 2)

    def _action_drag_toggle(self):
        if not self.dragging:
            mouse.press(Button.left)
            self.dragging = True
            print("拖拽模式开启")
        else:
            mouse.release(Button.left)
            self.dragging = False
            print("拖拽模式关闭")

    def _action_volume_up(self):
        pyautogui.press('volumeup')

    def _action_volume_down(self):
        pyautogui.press('volumedown')

    def _action_scroll_mode_toggle(self):
        self.scroll_mode_active = not self.scroll_mode_active
        state = "开启" if self.scroll_mode_active else "关闭"
        print(f"滚动模式{state}")

    def _action_stop(self):
        self.scroll_mode_active = False
        self.dragging = False
        if self.mouse_hold_start_pos:
            mouse.release(Button.left)
            self.mouse_hold_start_pos = None
        print("所有操作已停止")

    def _action_screenshot(self):
        screenshot = pyautogui.screenshot()
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        print(f"截图已保存为 {filename}")

    # --- 动态手势动作 ---
    def _action_back(self):
        pyautogui.hotkey('alt', 'left')

    def _action_forward(self):
        pyautogui.hotkey('alt', 'right')

    def _action_switch_window(self):
        pyautogui.hotkey('alt', 'tab')