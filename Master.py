import mss.tools
import time
from threading import Thread
import ColorConversion as cc
import PixelReader as PR
import Data
import Movement
import Inputter

# start_time = time.time()
# inp = Inputter.Inputter("World of Warcraft")
#
# sct = mss.mss()
# all = sct.monitors
# Timeout = 5000
# Time = 0
# colors = cc.StringToColor("bob")
# colors_integers = (int(colors[0] * 255), int(colors[1] * 255), int(colors[2] * 255))
# backstring = cc.ColorToString(*colors_integers)
# assert (backstring == "BOB")


## RGB: Red upper hex, green middle hex, blue lower hex: #FF0000 red, #00FF00 green, #0000FF blue

# ACCOUNT: asdf:fdsa

def FightDruid():
    print("Fighting")
    prev_pos = (Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD)
    is_moving = False
    while Data.PLAYER_IN_COMBAT or Data.PLAYER_CASTING_SPELL:
        time.sleep(0.10)
        if Data.PLAYER_CASTING_SPELL:
            continue
        if Data.PLAYER_RANGE > 30:
            inp.tapkey(Data.KEY_INTERACT_WITH_TARGET)
            is_moving = True
            continue
        # What if we're still moving?
        if is_moving and (Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD) != prev_pos:
            inp.tapkey('s')
            is_moving = False
        prev_pos = (Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD)
        if Data.PLAYER_HEALTH_CURR < Data.PLAYER_HEALTH_MAX * 0.30:
            inp.tapkey('num2')
            continue
        if not Data.TARGET_IN_COMBAT or not Data.TARGET_ATTACKING_PLAYER:
        # Try to find the reason we're in combat
            print("finding new target, not in combat with current...")
            inp.tapkey('tab')
            continue
        inp.tapkey('num1')


# combopoints = GetComboPoints("player", "target")
def Fight():
    print("Fighting")
    no_energy_used_count = 0
    prev_energy = 100
    prev_pos = (Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD)

    while Data.PLAYER_IN_COMBAT:
        time.sleep(0.2)
        if not Data.TARGET_IN_COMBAT or not Data.TARGET_ATTACKING_PLAYER:
            # Try to find the reason we're in combat
            print("finding new target, not in combat with current...")
            inp.tapkey('tab')
            continue

            # Far away from target? Run towards it
        # inp.tapkey('0') # startattack
        # if Data.PLAYER_RANGE > 10:
        #    inp.tapkey(Data.KEY_INTERACT_WITH_TARGET)
        #    continue
        # We're within range.
        if prev_energy > 45:
            # if we reach this point we didnt do anything.. do we need to face enemy?
            no_energy_used_count += 1
            if no_energy_used_count > 2:
                inp.tapkey(Data.KEY_INTERACT_WITH_TARGET)
                no_energy_used_count = 0
        prev_energy = Data.PLAYER_MANA_CURR
        # What if we're still moving?
        if (Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD) != prev_pos:
            inp.tapkey('s')
        # Bandage on low health
        if Data.PLAYER_HEALTH_CURR < Data.PLAYER_HEALTH_MAX * 0.30:
            inp.tapkey('4')
            time.sleep(0.9)
            inp.tapkey('F7')
            time.sleep(1)
            continue
        if Data.PLAYER_COMBO_POINTS > 3:
            inp.tapkey('2')
            continue
        if Data.PLAYER_MANA_CURR > 45:
            inp.tapkey('1')
            continue


def RecentlyLeftCombat():
    print("Recently left combat")
    # Target last target:
    inp.tapkey(Data.KEY_TARGET_PREVIOUS_TARGET)
    time.sleep(1.0)
    currposX, currposY = Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD
    # loot
    for i in range(0, 4):
        inp.tapkey(Data.KEY_INTERACT_WITH_TARGET)
    while currposX != Data.PLAYER_X_COORD or currposY != Data.PLAYER_Y_COORD:
        currposX, currposY = Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD
        time.sleep(0.2)

    time.sleep(1.0)
    while Data.PLAYER_IS_LOOTING:
        if Data.PLAYER_IS_LOOTING_BOP:
            print("BOP, click somewhere!")
        pass
    if Data.PLAYER_HEALTH_CURR < Data.PLAYER_HEALTH_MAX * 0.70:
        print("Gotta eat")
        # PRESS FOOD HERE
        inp.tapkey('7')
        while Data.PLAYER_HEALTH_CURR < Data.PLAYER_HEALTH_MAX:
            pass
    incombat = False
    # inp.tapkey("esc")


def Pull():
    incombat = True
    # Check if in range and good target
    if Data.PLAYER_RANGE > 30:
        print("Far pull")
        while Data.PLAYER_RANGE > 30:
            inp.tapkey(Data.KEY_INTERACT_WITH_TARGET)
            time.sleep(0.1)
            print("Waiting to run closer")
            pass
    else:
        inp.tapkey(Data.KEY_INTERACT_WITH_TARGET)
    inp.tapkey('s')
    time.sleep(0.2)
    inp.tapkey('num1')
    time.sleep(0.2)
    # If we are casting spells, we gotta wait for spellcast and a few frames to update values
    if Data.PLAYER_CASTING_SPELL:
        while Data.PLAYER_CASTING_SPELL:
            pass
    time.sleep(0.5)


def ScanForTarget():
    # clear target
    # if Data.TARGET_IS_DEAD:
    #    inp.tapkey("esc")
    #    time.sleep(0.5)
    while Data.TARGET_HEALTH_CURR == 0:
        inp.tapkey('tab')


# thread1 = Thread(target=PR.thread_monitor, args=("Thread-1",))
# thread1.start()
# time.sleep(1)  # NECESSARY TO INITIALIZE ALL VARIABLES
#
# # Movement.recordMovement()
# # exit(0)
#
# path = Movement.readPath()
# thread2 = Thread(target=Movement.FollowPath, args=("Thread-2", path,))
# thread2.start()
# # Movement.recordMovement()
#
# # while True:
# #    pass
#
# incombat = False
#
# while True:
#     # print(str(Data.PLAYER_IN_COMBAT))
#     # pass
#     while Data.TARGET_HEALTH_CURR == 0 and not incombat:
#         ScanForTarget()
#         print("Waiting for target")
#     Movement.paused = True
#     Pull()
#     FightDruid()
#     RecentlyLeftCombat()
#     Movement.paused = False
#
# # Movement.recordMovement()
# path = Movement.readPath()
# Movement.FollowPath(path)
# exit(0)



if __name__ == "__main__":
    start_time = time.time()
    inp = Inputter.Inputter("World of Warcraft")

    sct = mss.mss()
    all = sct.monitors
    # Timeout = 5000
    # Time = 0
    # colors = cc.StringToColor("bob")
    # colors_integers = (int(colors[0] * 255), int(colors[1] * 255), int(colors[2] * 255))
    # backstring = cc.ColorToString(*colors_integers)
    # assert (backstring == "BOB")

    thread1 = Thread(target=PR.thread_monitor, args=("Thread-1",))
    thread1.start()
    time.sleep(1)  # NECESSARY TO INITIALIZE ALL VARIABLES


    path = Movement.readPath()
    thread2 = Thread(target=Movement.FollowPath, args=("Thread-2", path,))
    thread2.start()

    incombat = False
    while True:
        while Data.TARGET_HEALTH_CURR == 0 and not incombat:
            ScanForTarget()
            print("Waiting for target")
        Movement.paused = True
        Pull()
        FightDruid()
        RecentlyLeftCombat()
        Movement.paused = False