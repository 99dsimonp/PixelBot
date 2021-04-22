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

def IntegerToColor(i):
    if i != math.floor(i):
        print("Error!")
        return 0
    if i > 256*256*256 - 1:
        print("Error: Value too large!")
        return 0
    b = i % 256
    i = math.floor(i/256)
    g = i % 256
    i = math.floor(i/256)
    r = i % 256

    return (r/255, g/255, b/255)

def ColorToInteger(r,b,g):
    assert(0 <= r <= 255)
    assert(0 <= b <= 255)
    assert(0 <= g <= 255)
    hx = '%02x%02x%02x' % (r, b, g)
    return int(hx, 16)

def DecimalToColor(i):
    if i > 9.99999:
        print("Error: decimal too large")
        return 0
    if i < 0:
        print("Error: Decimal too small")
    i = math.floor(i*100000)
    return IntegerToColor(i)

def ColorToDecimal(r,b,g):
    intval = ColorToInteger(r,b,g)
    return intval / 100000


def StringToColor(input):
    input = input.upper()
    ascii_vals = ""
    for val in input[:3]:
        ascii_vals = ascii_vals + str(ord(val))
    intval = int(ascii_vals)
    return IntegerToColor(intval)

def ColorToString(r,b,g):
    intval = ColorToInteger(r,b,g)
    if intval > 999999:
        return None
    intstring = str(intval)
    string_output = ""
    for i in range(0, len(intstring), 2):
        string_output = string_output + chr(int(intstring[i:i+2]))
    return string_output

def is_set(val, bit):
    return val & 1 << bit != 0

def ColorToBool(r,b,g):
    intval = ColorToInteger(r,b,g)
    TARGET_IN_COMBAT = is_set(intval, 0)
    TARGET_IS_ENEMY = is_set(intval, 1)
    PLAYER_IS_DEAD = is_set(intval, 2)
    PLAYER_FREE_TALENT_POINTS = is_set(intval, 3)
    PLAYER_NEED_WATER = is_set(intval, 4)
    PLAYER_HAS_FOOD_BUFF = is_set(intval, 5)
    PLAYER_IN_FLIGHT = is_set(intval, 10)
    PLAYER_EATING = is_set(intval, 13)
    PLAYER_IN_COMBAT = is_set(intval, 14)
    TARGET_ATTACKING_PLAYER = is_set(intval, 15)
    return TARGET_IN_COMBAT, TARGET_IS_ENEMY, PLAYER_IS_DEAD, PLAYER_FREE_TALENT_POINTS, PLAYER_NEED_WATER, PLAYER_HAS_FOOD_BUFF, PLAYER_IN_FLIGHT, PLAYER_EATING, PLAYER_IN_COMBAT, TARGET_ATTACKING_PLAYER


PIXEL_PLAYER_X_COORD = (8, 25)
PIXEL_PLAYER_Y_COORD = (13, 25)
PIXEL_PLAYER_FACING = (18, 25)
PIXEL_ZONE_FIRSTNAME = (23, 25)
PIXEL_ZONE_SECONDNAME = (28, 25)
PIXEL_PLAYER_CORPSE_X_COORD = (33, 25)
PIXEL_PLAYER_CORPSE_Y_COORD = (38, 25)
PIXEL_PLAYER_BOOLEAN_VAR = (43, 25)
PIXEL_PLAYER_HEALTH_MAX = (55, 25)
PIXEL_PLAYER_HEALTH_CURR = (58, 25)
PIXEL_PLAYER_MANA_MAX = (63, 25)
PIXEL_PLAYER_MANA_CURR = (68, 25)
PIXEL_PLAYER_LEVEL = (73, 25)
PIXEL_PLAYER_RANGE = (78, 25)
PIXEL_TARGET_NAMEFIRST = (83, 25)
PIXEL_TARGET_NAMESECOND = (88, 25)
PIXEL_TARGET_HEALTH_MAX = (93, 25)
PIXEL_TARGET_HEALTH_CURR = (98, 25)
start_time = time.time()


sct = mss.mss()
all = sct.monitors
#img = np.array(0)
Timeout = 5000
Time = 0
colors  = StringToColor("bob")
colors_integers = (int(colors[0]*255), int(colors[1]*255), int(colors[2]*255))
backstring = ColorToString(*colors_integers)
assert(backstring == "BOB")
## RGB: Red upper hex, green middle hex, blue lower hex: #FF0000 red, #00FF00 green, #0000FF blue

#FIND NAME:
scr2 = sct.grab({"mon": 2, "top": 0,"left": 0, "width": 300, "height": 30})
img = np.array(scr2)
PLAYER_X_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_X_COORD))
PLAYER_Y_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_Y_COORD))
PLAYER_FACING = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_FACING))
ZONE_FIRSTNAME = ColorToString(*scr2.pixel(*PIXEL_ZONE_FIRSTNAME))
ZONE_SECONDNAME = ColorToString(*scr2.pixel(*PIXEL_ZONE_SECONDNAME))
PLAYER_CORPSE_X_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_CORPSE_X_COORD))
PLAYER_CORPSE_Y_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_CORPSE_Y_COORD))
TARGET_IN_COMBAT, TARGET_IS_ENEMY, PLAYER_IS_DEAD, PLAYER_FREE_TALENT_POINTS, PLAYER_NEED_WATER, PLAYER_HAS_FOOD_BUFF, PLAYER_IN_FLIGHT, PLAYER_EATING, PLAYER_IN_COMBAT, TARGET_ATTACKING_PLAYER = ColorToBool(*scr2.pixel(*PIXEL_PLAYER_BOOLEAN_VAR))
PLAYER_HEALTH_MAX = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_HEALTH_MAX))
PLAYER_HEALTH_CURR = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_HEALTH_CURR))
PLAYER_MANA_MAX = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_MANA_MAX))
PLAYER_MANA_CURR = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_MANA_CURR))
PLAYER_LEVEL = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_LEVEL))
PLAYER_RANGE = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_RANGE))
TARGET_NAMEFIRST = ColorToString(*scr2.pixel(*PIXEL_TARGET_NAMEFIRST))
TARGET_NAMESECOND = ColorToString(*scr2.pixel(*PIXEL_TARGET_NAMESECOND))
TARGET_HEALTH_MAX = ColorToInteger(*scr2.pixel(*PIXEL_TARGET_HEALTH_MAX))
TARGET_HEALTH_CURR = ColorToInteger(*scr2.pixel(*PIXEL_TARGET_HEALTH_CURR))

#ACCOUNT: asdf:fdsa

#combopoints = GetComboPoints("player", "target")
def Fight():
    global PLAYER_IN_COMBAT
    global PLAYER_RANGE
    global TARGET_ATTACKING_PLAYER
    while PLAYER_IN_COMBAT:
        if not TARGET_ATTACKING_PLAYER:
            #Try to find the reason we're in combat
            pyautogui.press('tab')
            continue
        if PLAYER_RANGE > 10:
            pyautogui.press('å')
            continue
        if PLAYER_MANA_CURR > 45:
            pyautogui.press('1')


def Turn(goal_radians): #https://math.stackexchange.com/questions/2062021/finding-the-angle-between-a-point-and-another-point-with-an-angle
    #Turn speed: pi radians per second
    #TURN RIGHT (d) DECREASES ANGLE
    #TURNING LEFT (a) INCREASES ANGLE
    #1. Increase angle over 2pi and reach aim
    if PLAYER_FACING > goal_radians and PLAYER_FACING > math.pi and (PLAYER_FACING + math.pi) % 2* math.pi > goal_radians:
        print("Facing 1")
        target = goal_radians + 2*math.pi
        pyautogui.keyDown('a')
        sleeptime = (target-PLAYER_FACING)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('a')
        return
    #2. Increase angle up to goal
    elif PLAYER_FACING < goal_radians and PLAYER_FACING + math.pi > goal_radians:
        print("Facing 2")
        pyautogui.keyDown('a')
        sleeptime = (goal_radians - PLAYER_FACING)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('a')
        return
    #3. Reduce angle down to goal
    elif PLAYER_FACING > goal_radians and PLAYER_FACING-goal_radians < math.pi:
        print("Facing3")
        pyautogui.keyDown('d')
        sleeptime = (PLAYER_FACING - goal_radians)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('d')
    #4. Reduce angle below 0 to overflow
    else: #if PLAYER_FACING < goal_radians and PLAYER_FACING + math.pi*2 < goal_radians:
        print("Facing4")
        pyautogui.keyDown('d')
        sleeptime = (PLAYER_FACING+ 2*math.pi -  goal_radians)/math.pi
        assert(0 < sleeptime < 2)
        time.sleep(sleeptime)
        pyautogui.keyUp('d')
    #else:
    #    print("How did we get here?")
        #error = math.fabs(PLAYER_FACING - goal_radians)
        #while error > 0.2:
        #    pyautogui.keyDown('a')
        #    error = math.fabs(PLAYER_FACING - goal_radians)
        #    print(str(error))
        #pyautogui.keyUp('a')


def MoveTo(X, Y):
    new_facing_direction = math.atan2( X - PLAYER_X_COORD, Y- PLAYER_Y_COORD) + math.pi
    if new_facing_direction < 0:
        #new_facing_direction = (2 *math.pi - new_facing_direction) % 2*math.pi
        new_facing_direction = new_facing_direction + math.pi
    Turn(new_facing_direction)
    placement_error = (max(PLAYER_X_COORD, X) - min(PLAYER_X_COORD, X)) + (max(PLAYER_Y_COORD, Y) - min(PLAYER_Y_COORD, Y))
    #placement_error = math.sqrt(math.pow(X-PLAYER_X_COORD - X,2) + math.pow(Y-PLAYER_CORPSE_Y_COORD,2))
    prev_error = placement_error
    while placement_error > 0.0007:
        pyautogui.keyDown('w')
        prev_error = placement_error
        placement_error = (max(PLAYER_X_COORD, X) - min(PLAYER_X_COORD, X)) + (max(PLAYER_Y_COORD, Y) - min(PLAYER_Y_COORD, Y))
        if prev_error < placement_error:
            new_facing_direction = math.atan2(Y-PLAYER_Y_COORD, X - PLAYER_X_COORD )
            if new_facing_direction < 0:
                new_facing_direction = (2 *math.pi - new_facing_direction) % 2*math.pi
            pyautogui.keyUp('w')
            Turn(new_facing_direction)
            pyautogui.keyDown('w')
        print(placement_error)
    pyautogui.keyUp('w')

# PIXELS WITH DATA WHEN WINDOWED MODE:
# i= 23-27, j=21-25 ALL VALUES INCLUSIVE
# i= 23-27, j=26-30
# print(ColorToString(*scr2.pixel(30, 27)))
# print(ColorToInteger(*scr2.pixel(*PLAYER_HEALTH_MAX)))

def thread_monitor(threadname):
    global PLAYER_X_COORD
    global PLAYER_Y_COORD
    global PLAYER_FACING
    global ZONE_FIRSTNAME
    global ZONE_SECONDNAME
    global PLAYER_CORPSE_X_COORD
    global PLAYER_CORPSE_Y_COORD
    global PLAYER_BOOLEAN_VAR
    global PLAYER_HEALTH_MAX
    global PLAYER_HEALTH_CURR
    global PLAYER_MANA_MAX
    global PLAYER_MANA_CURR
    global PLAYER_LEVEL
    global PLAYER_RANGE
    global TARGET_NAMEFIRST
    global TARGET_NAMESECOND
    global TARGET_HEALTH_MAX
    global TARGET_HEALTH_CURR
    global TARGET_IN_COMBAT
    global TARGET_IS_ENEMY
    global PLAYER_IS_DEAD
    global PLAYER_FREE_TALENT_POINTS
    global PLAYER_NEED_WATER
    global PLAYER_HAS_FOOD_BUFF
    global PLAYER_IN_FLIGHT
    global PLAYER_EATING
    global PLAYER_IN_COMBAT
    global TARGET_ATTACKING_PLAYER
    while True:
        scr2 = sct.grab({"mon": 2, "top": 0,"left": 0, "width": 300, "height": 30})
        PLAYER_X_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_X_COORD))
        PLAYER_Y_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_Y_COORD))
        PLAYER_FACING = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_FACING))
        ZONE_FIRSTNAME = ColorToString(*scr2.pixel(*PIXEL_ZONE_FIRSTNAME))
        ZONE_SECONDNAME = ColorToString(*scr2.pixel(*PIXEL_ZONE_SECONDNAME))
        PLAYER_CORPSE_X_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_CORPSE_X_COORD))
        PLAYER_CORPSE_Y_COORD = ColorToDecimal(*scr2.pixel(*PIXEL_PLAYER_CORPSE_Y_COORD))
        PLAYER_BOOLEAN_VAR = ColorToBool(*scr2.pixel(*PIXEL_PLAYER_BOOLEAN_VAR))
        PLAYER_HEALTH_MAX = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_HEALTH_MAX))
        PLAYER_HEALTH_CURR = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_HEALTH_CURR))
        PLAYER_MANA_MAX = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_MANA_MAX))
        PLAYER_MANA_CURR = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_MANA_CURR))
        PLAYER_LEVEL = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_LEVEL))
        PLAYER_RANGE = ColorToInteger(*scr2.pixel(*PIXEL_PLAYER_RANGE))
        TARGET_NAMEFIRST = ColorToString(*scr2.pixel(*PIXEL_TARGET_NAMEFIRST))
        TARGET_NAMESECOND = ColorToString(*scr2.pixel(*PIXEL_TARGET_NAMESECOND))
        TARGET_HEALTH_MAX = ColorToInteger(*scr2.pixel(*PIXEL_TARGET_HEALTH_MAX))
        TARGET_HEALTH_CURR = ColorToInteger(*scr2.pixel(*PIXEL_TARGET_HEALTH_CURR))
        TARGET_IN_COMBAT, TARGET_IS_ENEMY, PLAYER_IS_DEAD, PLAYER_FREE_TALENT_POINTS, PLAYER_NEED_WATER, PLAYER_HAS_FOOD_BUFF, PLAYER_IN_FLIGHT, PLAYER_EATING, PLAYER_IN_COMBAT, TARGET_ATTACKING_PLAYER = ColorToBool(*scr2.pixel(*PIXEL_PLAYER_BOOLEAN_VAR))
        #... add more


thread1 = Thread( target=thread_monitor, args=("Thread-1", ) )
thread1.start()

#while True:
#1    print(str(PLAYER_RANGE))

Fight()
MoveTo(0.60922724,0.533741176)
#Turn(4.73178)

while True:
    #scr = sct.shot(mon=2, output='fullscreen-wow.jpg')
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

