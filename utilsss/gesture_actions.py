import pyautogui

def run_action(gesture):

    if gesture=="click":
        pyautogui.click()

    elif gesture=="right_click":
        pyautogui.click(button="right")

    elif gesture=="double_click":
        pyautogui.doubleClick()

    elif gesture=="scroll_up":
        pyautogui.scroll(20)

    elif gesture=="scroll_down":
        pyautogui.scroll(-20)

    elif gesture=="volume_up":
        pyautogui.press("volumeup")

    elif gesture=="volume_down":
        pyautogui.press("volumedown")

    elif gesture=="screenshot":
        pyautogui.screenshot("shot.png")