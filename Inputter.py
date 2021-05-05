import time
import win32gui, win32ui, win32con, win32api

def translate_key(key):
    if len(key) > 1:
        if key =='tab':
            key = 0x09
        elif key =="esc":
            key = 0x1B
        elif key == "space":
            key = 0x20
        if key[:3] == "num":
            key = 0x60 + int(key[3])
    else:
        key = ord(str(key).upper())
    return key


class Inputter:
    debugging = False
    hwnd = None

    def __init__(self, window_name):
        # find the handle for the window we want to capture
        self.hwnd = win32gui.FindWindow(None, window_name)

    def keydown(self, key):
        key = translate_key(key)
        if not self.debugging:
            win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
            #pyautogui.keyDown(key)

    def keyup(self, key):
        key = translate_key(key)
        if not self.debugging:
            win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, key, 0)
            #pyautogui.keyUp(key)

    def tapkey(self, key):
        key = translate_key(key)

        if not self.debugging:
            win32gui.SendMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
            win32gui.SendMessage(self.hwnd, win32con.WM_KEYUP, key, 0)