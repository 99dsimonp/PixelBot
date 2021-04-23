import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
#from PIL import Image
import mss
import mss.tools
import pyautogui
import time
#import sounddevice as sd
import queue
import pyaudio
import struct
import math
import wave
import random
from threading import Thread
import ColorConversion as cc
import PixelReader as PR
import Data
import Display
import Movement

start_time = time.time()



sct = mss.mss()
all = sct.monitors
#img = np.array(0)
Timeout = 5000
Time = 0
colors = cc.StringToColor("bob")
colors_integers = (int(colors[0]*255), int(colors[1]*255), int(colors[2]*255))
backstring = cc.ColorToString(*colors_integers)
assert(backstring == "BOB")
## RGB: Red upper hex, green middle hex, blue lower hex: #FF0000 red, #00FF00 green, #0000FF blue

#ACCOUNT: asdf:fdsa

#combopoints = GetComboPoints("player", "target")
def Fight():
    while Data.PLAYER_IN_COMBAT:
        if not Data.TARGET_ATTACKING_PLAYER:
            #Try to find the reason we're in combat
            pyautogui.press('tab')
            continue
        if Data.PLAYER_RANGE > 10:
            pyautogui.press('å')
            continue
        if Data.PLAYER_HEALTH_CURR < Data.PLAYER_HEALTH_MAX*0.30:
            pyautogui.press('4')
            time.sleep(0.9)
            pyautogui.press('F7')
            time.sleep(1)
        if Data.PLAYER_COMBO_POINTS > 3:
            pyautogui.press('2')
        if Data.PLAYER_MANA_CURR > 45:
            pyautogui.press('1')


# PIXELS WITH DATA WHEN WINDOWED MODE:
# i= 23-27, j=21-25 ALL VALUES INCLUSIVE
# i= 23-27, j=26-30
# print(ColorToString(*scr2.pixel(30, 27)))
# print(ColorToInteger(*scr2.pixel(*PLAYER_HEALTH_MAX)))


thread1 = Thread( target=PR.thread_monitor, args=("Thread-1", ) )
thread1.start()

#thread2 = Thread( target=Display.run, args=("Thread-2", ) )
#thread2.start() #Displaying things, how?

#while True:
#    print(str(Data.PLAYER_X_COORD))
#Movement.recordMovement()
path = Movement.readPath()
Movement.FollowPath(path)
exit(0)

time.sleep(1)

#Fight()
Movement.MoveTo(0.50800329446793, 0.28960570693016, 'fine')

while True:
    print(str(Data.PLAYER_X_COORD))
#MoveTo(0.50800329446793, 0.28960570693016)
#Turn(4.73178)

while True:
    #scr = sct.shot(mon=2, outpuwt='fullscreen-wow.jpg')
    #scr1 = sct.grab({"mon": 2, "top": 0,"left": 0, "width": 2560, "height": 1440})
    #scr2 = sct.grab({"mon": 2, "top": 0,"left": 0, "width": 300, "height": 30})
    #mss.tools.to_png(scr2.rgb, scr2.size, output="pixels.png")
    #img = np.array(scr1) # [height][width]
    #img2 = cv.imread('fullscreen-wow.jpg', 0)

    #print("--- %s seconds ---" % (time.time() - start_time))
    #print("Health:" + str(PLAYER_HEALTH_CURR) + "/" + str(PLAYER_HEALTH_MAX))
    print("X/Y:" + str(PLAYER_X_COORD) + "/" + str(PLAYER_Y_COORD) + ": DIR" + str(PLAYER_FACING))

    if cv.waitKey(25) & 0xFF == ord("x"):
        break
    #time.sleep(4)
    continue

    #img2 = img.copy()
    template = cv.imread('bobber.jpg', 0)
    w, h = template.shape[::-1]
    methods = ['cv.TM_CCOEFF_NORMED']#, 'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
    for meth in methods:
        method = eval(meth)
        # Apply template Matching
        res = cv.matchTemplate(img,template,method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        mid = (top_left[0] + w/2, top_left[1] + h/2)
        mid_moveto = (mid[0] + random.randint(0, 5), mid[1] + random.randint(0,5))
        pyautogui.moveTo(mid_moveto)
        q = queue.Queue()

