import ColorConversion as cc
import mss
import Data
import math
import win32gui, win32ui, win32con
import numpy as np
import cv2 as cv
import numpy as np
import os
import time

class WindowCapture:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name):
        # find the handle for the window we want to capture
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = int((window_rect[2] - window_rect[0])/1.4)
        self.h = int((window_rect[3] - window_rect[1])/2)

        # account for the window border and titlebar and cut them off
        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):
        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type()
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    def list_window_names(self):
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)




PIXEL_PLAYER_X_COORD = (8, 1)
PIXEL_PLAYER_Y_COORD = (13, 1)
PIXEL_PLAYER_FACING = (18, 1)
PIXEL_ZONE_FIRSTNAME = (23, 1)
PIXEL_ZONE_SECONDNAME = (28, 1)
PIXEL_PLAYER_CORPSE_X_COORD = (33, 1)
PIXEL_PLAYER_CORPSE_Y_COORD = (38, 1)
PIXEL_PLAYER_BOOLEAN_VAR = (43, 1)
PIXEL_PLAYER_HEALTH_MAX = (55, 1)
PIXEL_PLAYER_HEALTH_CURR = (58, 1)
PIXEL_PLAYER_MANA_MAX = (63, 1)
PIXEL_PLAYER_MANA_CURR = (68, 1)
PIXEL_PLAYER_LEVEL = (73, 1)
PIXEL_PLAYER_RANGE = (78, 1)
PIXEL_TARGET_NAMEFIRST = (83, 1)
PIXEL_TARGET_NAMESECOND = (88, 1)
PIXEL_TARGET_HEALTH_MAX = (93, 1)
PIXEL_TARGET_HEALTH_CURR = (98, 1)
PIXEL_IS_LOOTING_BOP = (1431, 251)
PIXEL_IS_LOOTING_BOE = (207, 326)
PIXEL_LOOT_COLOR = (128, 26, 204) # screenshot: [204, 26, 128]

def get_pixel_color(screenshot, pixel_width, pixel_height):
    result = screenshot[pixel_height][pixel_width]
    return (result[2], result[1], result[0])


def thread_monitor(threadname):
    wincap = WindowCapture('World of Warcraft')
    #sct = mss.mss()
    while True:
        screenshot = wincap.get_screenshot()
        #scr2 = sct.grab({"mon": 2, "top": 0, "left": 0, "width": 1432, "height": 351})
        Data.PLAYER_X_COORD = cc.ColorToDecimal(*get_pixel_color(screenshot, *PIXEL_PLAYER_X_COORD))
        Data.PLAYER_Y_COORD = cc.ColorToDecimal(*get_pixel_color(screenshot, *PIXEL_PLAYER_Y_COORD))
        Data.PLAYER_FACING = cc.ColorToDecimal(*get_pixel_color(screenshot, *PIXEL_PLAYER_FACING))
        Data.ZONE_FIRSTNAME = cc.ColorToString(*get_pixel_color(screenshot, *PIXEL_ZONE_FIRSTNAME))
        Data.ZONE_SECONDNAME = cc.ColorToString(*get_pixel_color(screenshot, *PIXEL_ZONE_SECONDNAME))
        Data.PLAYER_CORPSE_X_COORD = cc.ColorToDecimal(*get_pixel_color(screenshot, *PIXEL_PLAYER_CORPSE_X_COORD))
        Data.PLAYER_CORPSE_Y_COORD = cc.ColorToDecimal(*get_pixel_color(screenshot, *PIXEL_PLAYER_CORPSE_Y_COORD))
        Data.PLAYER_HEALTH_MAX = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_PLAYER_HEALTH_MAX))
        Data.PLAYER_HEALTH_CURR = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_PLAYER_HEALTH_CURR))
        Data.PLAYER_MANA_MAX = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_PLAYER_MANA_MAX))
        Data.PLAYER_MANA_CURR = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_PLAYER_MANA_CURR))
        Data.PLAYER_LEVEL = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_PLAYER_LEVEL))
        Data.PLAYER_RANGE = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_PLAYER_RANGE))
        Data.TARGET_NAMEFIRST = cc.ColorToString(*get_pixel_color(screenshot, *PIXEL_TARGET_NAMEFIRST))
        Data.TARGET_NAMESECOND = cc.ColorToString(*get_pixel_color(screenshot, *PIXEL_TARGET_NAMESECOND))
        Data.TARGET_HEALTH_MAX = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_TARGET_HEALTH_MAX))
        Data.TARGET_HEALTH_CURR = cc.ColorToInteger(*get_pixel_color(screenshot, *PIXEL_TARGET_HEALTH_CURR))
        Data.TARGET_IN_COMBAT, Data.TARGET_IS_DEAD, Data.PLAYER_IS_DEAD, Data.PLAYER_NUM_FREE_TALENT_POINTS, Data.PLAYER_NEEDS_TO_BUY_WATER, Data.PLAYER_HAS_FOOD_BUFF, Data.PLAYER_COMBO_POINTS, \
        Data.PLAYER_IN_STEALTH, Data.PLAYER_ICE_BARRIER, Data.PLAYER_HAS_BROKEN_EQUIPMENT, Data.PLAYER_IN_FLIGHT, Data.PLAYER_NEEDS_TO_BUY_FOOD, \
        Data.PLAYER_CASTING_SPELL, Data.PLAYER_HAS_DRINK_BUFF, Data.PLAYER_IN_COMBAT, Data.TARGET_ATTACKING_PLAYER, Data.PLAYER_CHANNELING_SPELL, Data.PROCESS_EXIT_STATUS = cc.ColorToBool(*get_pixel_color(screenshot, *PIXEL_PLAYER_BOOLEAN_VAR))
        Data.PLAYER_IS_LOOTING = get_pixel_color(screenshot, *PIXEL_IS_LOOTING_BOE) != PIXEL_LOOT_COLOR
        Data.PLAYER_IS_LOOTING_BOP = get_pixel_color(screenshot, *PIXEL_IS_LOOTING_BOP) != PIXEL_LOOT_COLOR
        #... add more

if __name__=="__main__":
    #thread_monitor(1)
    start_time = time.time()
    # initialize the WindowCapture class
    wincap = WindowCapture('World of Warcraft')

    loop_time = time.time()
    while(True):
        time.sleep(0.01)

        # get an updated image of the game
        screenshot = wincap.get_screenshot()

        cv.imshow('Computer Vision', screenshot)

        # debug the loop rate
        print('FPS {}'.format(1 / (time.time() - loop_time)))
        loop_time = time.time()

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    print('Done.')