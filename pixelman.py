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

# PIXEL_PLAYER_X_COORD = (8, 25)
# PIXEL_PLAYER_Y_COORD = (13, 25)
# PIXEL_PLAYER_FACING = (18, 25)
# PIXEL_ZONE_FIRSTNAME = (23, 25)
# PIXEL_ZONE_SECONDNAME = (28, 25)
# PIXEL_PLAYER_CORPSE_X_COORD = (33, 25)
# PIXEL_PLAYER_CORPSE_Y_COORD = (38, 25)
# PIXEL_PLAYER_BOOLEAN_VAR = (43, 25)
# PIXEL_PLAYER_HEALTH_MAX = (55, 25)
# PIXEL_PLAYER_HEALTH_CURR = (58, 25)
# PIXEL_PLAYER_MANA_MAX = (63, 25)
# PIXEL_PLAYER_MANA_CURR = (68, 25)
# PIXEL_PLAYER_LEVEL = (73, 25)
# PIXEL_PLAYER_RANGE = (78, 25)
# PIXEL_TARGET_NAMEFIRST = (83, 25)
# PIXEL_TARGET_NAMESECOND = (88, 25)
# PIXEL_TARGET_HEALTH_MAX = (93, 25)
# PIXEL_TARGET_HEALTH_CURR = (98, 25)
# PIXEL_IS_LOOTING_BOP = (1280+90, 720+270)
# PIXEL_IS_LOOTING_BOE = (120, 200)
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
        if Data.PLAYER_MANA_CURR > 45:
            pyautogui.press('1')


def Turn(goal_radians): #https://math.stackexchange.com/questions/2062021/finding-the-angle-between-a-point-and-another-point-with-an-angle
    #Turn speed: pi radians per second
    #TURN RIGHT (d) DECREASES ANGLE
    #TURNING LEFT (a) INCREASES ANGLE
    #1. Increase angle over 2pi and reach aim
    print("New goal:" + str(goal_radians))
    curr_PLAYER_FACING = Data.PLAYER_FACING
    #3. Reduce angle down to goal
    if curr_PLAYER_FACING > goal_radians and curr_PLAYER_FACING-goal_radians < math.pi:
        print("Facing3")
        pyautogui.keyDown('d')
        sleeptime = (curr_PLAYER_FACING - goal_radians)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('d')
    #2. Increase angle up to goal
    elif curr_PLAYER_FACING < goal_radians and curr_PLAYER_FACING + math.pi > goal_radians:
        print("Facing 2")
        pyautogui.keyDown('a')
        sleeptime = (goal_radians - curr_PLAYER_FACING)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('a')
        return
    elif curr_PLAYER_FACING > goal_radians and curr_PLAYER_FACING > math.pi and (curr_PLAYER_FACING + math.pi) % 2* math.pi > goal_radians:
        print("Facing 1")
        target = goal_radians + 2*math.pi
        pyautogui.keyDown('a')
        sleeptime = (target-Data.PLAYER_FACING)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('a')
        return
    #4. Reduce angle below 0 to overflow
    else: #if PLAYER_FACING < goal_radians and PLAYER_FACING + math.pi*2 < goal_radians:
        print("Facing4")
        pyautogui.keyDown('d')
        sleeptime = (curr_PLAYER_FACING+ 2*math.pi - goal_radians)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('d')


def MoveTo(X, Y):
    new_facing_direction = math.atan2(Y - Data.PLAYER_Y_COORD, Data.PLAYER_X_COORD - X )
    #slope is the absolute direction to the next point from the player
    new_facing_direction += math.pi # map to 0-2PI range
    #Rotate by 90 degrees (so that 0 is up, not right)
    new_facing_direction -= math.pi * 0.5
    #Ensures that slope is not less than 0
    if new_facing_direction < 0:
        new_facing_direction += math.pi *2
    #Ensures slope is not greater than 2p
    if new_facing_direction > math.pi*2:
        new_facing_direction -= math.pi*2
    
    Turn(new_facing_direction)
    placement_error = (max(Data.PLAYER_X_COORD, X) - min(Data.PLAYER_X_COORD, X)) + (max(Data.PLAYER_Y_COORD, Y) - min(Data.PLAYER_Y_COORD, Y))
    #placement_error = math.sqrt(math.pow(X-PLAYER_X_COORD - X,2) + math.pow(Y-PLAYER_CORPSE_Y_COORD,2))
    prev_error = placement_error
    while placement_error > 0.0007:
        pyautogui.keyDown('w')
        prev_error = placement_error
        placement_error = (max(Data.PLAYER_X_COORD, X) - min(Data.PLAYER_X_COORD, X)) + (max(Data.PLAYER_Y_COORD, Y) - min(Data.PLAYER_Y_COORD, Y))
        if prev_error < placement_error:
            pyautogui.keyUp('w')
            time.sleep(0.1)
            new_facing_direction = math.atan2(Y-Data.PLAYER_Y_COORD, X - Data.PLAYER_X_COORD )
            if new_facing_direction < 0:
                new_facing_direction = (2 *math.pi - new_facing_direction) % 2*math.pi
            Turn(new_facing_direction)
            pyautogui.keyDown('w')
        #print(placement_error)
    pyautogui.keyUp('w')

# PIXELS WITH DATA WHEN WINDOWED MODE:
# i= 23-27, j=21-25 ALL VALUES INCLUSIVE
# i= 23-27, j=26-30
# print(ColorToString(*scr2.pixel(30, 27)))
# print(ColorToInteger(*scr2.pixel(*PLAYER_HEALTH_MAX)))

# def thread_monitor(threadname):
#     global PLAYER_X_COORD
#     global PLAYER_Y_COORD
#     global PLAYER_FACING
#     global ZONE_FIRSTNAME
#     global ZONE_SECONDNAME
#     global PLAYER_CORPSE_X_COORD
#     global PLAYER_CORPSE_Y_COORD
#     global PLAYER_BOOLEAN_VAR
#     global PLAYER_HEALTH_MAX
#     global PLAYER_HEALTH_CURR
#     global PLAYER_MANA_MAX
#     global PLAYER_MANA_CURR
#     global PLAYER_LEVEL
#     global PLAYER_RANGE
#     global TARGET_NAMEFIRST
#     global TARGET_NAMESECOND
#     global TARGET_HEALTH_MAX
#     global TARGET_HEALTH_CURR
#     global TARGET_IN_COMBAT
#     global TARGET_IS_ENEMY
#     global PLAYER_IS_DEAD
#     global PLAYER_FREE_TALENT_POINTS
#     global PLAYER_NEED_WATER
#     global PLAYER_HAS_FOOD_BUFF
#     global PLAYER_IN_FLIGHT
#     global PLAYER_EATING
#     global PLAYER_IN_COMBAT
#     global TARGET_ATTACKING_PLAYER
#     while True:
#         scr2 = sct.grab({"mon": 2, "top": 0,"left": 0, "width": 300, "height": 30})
#         PLAYER_X_COORD = cc.ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_X_COORD))
#         PLAYER_Y_COORD = cc.ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_Y_COORD))
#         PLAYER_FACING = cc.ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_FACING))
#         ZONE_FIRSTNAME = cc.ColorToString(*scr2.pixel(*PIXEL_ZONE_FIRSTNAME))
#         ZONE_SECONDNAME = cc.ColorToString(*scr2.pixel(*PIXEL_ZONE_SECONDNAME))
#         PLAYER_CORPSE_X_COORD = cc.ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_CORPSE_X_COORD))
#         PLAYER_CORPSE_Y_COORD = cc.ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_CORPSE_Y_COORD))
#         PLAYER_BOOLEAN_VAR = ColorToBool(*scr2.pixel(*PIXEL_PLAYER_BOOLEAN_VAR))
#         PLAYER_HEALTH_MAX = cc.ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_HEALTH_MAX))
#         PLAYER_HEALTH_CURR = cc.ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_HEALTH_CURR))
#         PLAYER_MANA_MAX = cc.ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_MANA_MAX))
#         PLAYER_MANA_CURR = cc.ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_MANA_CURR))
#         PLAYER_LEVEL = cc.ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_LEVEL))
#         PLAYER_RANGE = cc.ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_RANGE))
#         TARGET_NAMEFIRST = cc.ColorToString(*scr2.pixel(*PIXEL_TARGET_NAMEFIRST))
#         TARGET_NAMESECOND = cc.ColorToString(*scr2.pixel(*PIXEL_TARGET_NAMESECOND))
#         TARGET_HEALTH_MAX = cc.ColorToInteger(*scr2.pixel(*PIXEL_TARGET_HEALTH_MAX))
#         TARGET_HEALTH_CURR = cc.ColorToInteger(*scr2.pixel(*PIXEL_TARGET_HEALTH_CURR))
#         TARGET_IN_COMBAT, TARGET_IS_ENEMY, PLAYER_IS_DEAD, PLAYER_FREE_TALENT_POINTS, PLAYER_NEED_WATER, PLAYER_HAS_FOOD_BUFF, PLAYER_IN_FLIGHT, PLAYER_EATING, PLAYER_IN_COMBAT, TARGET_ATTACKING_PLAYER = ColorToBool(*scr2.pixel(*PIXEL_PLAYER_BOOLEAN_VAR))
#         #... add more


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

