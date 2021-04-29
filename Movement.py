import math
import pyautogui
import Data
import time
import threading
import pickle

default = {
    "NEAREST_POINT_THRESHOLD": 0.3,
    "NAVIGATION_FUNCTION_INTERVAL": 10,
    "POINT_DISTANCE_ERROR": 0.007,
    "POINT_FINE_DISTANCE_ERROR": 0.003,
    "TURN_TIME_FACTOR": 878.333333,
    "CORRECTING_TURN_TIME_FACTOR": 2000, #was 400, takes 2 sec for full turn
    "MINIMUM_CORRECTING_TURN_TIME_MS": 200,
    "MINIMUM_TURN_TIME_MS": 100
}

special = {
    "NEAREST_POINT_THRESHOLD": 0.3,
    "NAVIGATION_FUNCTION_INTERVAL": 10,
    "POINT_DISTANCE_ERROR": 0.030,
    "POINT_FINE_DISTANCE_ERROR": 0.009,
    "TURN_TIME_FACTOR": 878.333333,
    "CORRECTING_TURN_TIME_FACTOR": 400,
    "MINIMUM_CORRECTING_TURN_TIME_MS": 200,
    "MINIMUM_TURN_TIME_MS": 100
}
city = {
    "NEAREST_POINT_THRESHOLD": 0.3,
    "NAVIGATION_FUNCTION_INTERVAL": 10,
    "POINT_DISTANCE_ERROR": 0.050,
    "POINT_FINE_DISTANCE_ERROR": 0.009,
    "TURN_TIME_FACTOR": 878.333333,
    "CORRECTING_TURN_TIME_FACTOR": 400,
    "MINIMUM_CORRECTING_TURN_TIME_MS": 200,
    "MINIMUM_TURN_TIME_MS": 100
}
unstuck = {
    "STUCK_DISTANCE": 0.0002,
    "STUCK_BACKWARDS_UPDATES_COUNT": 20,
    "BLINK_WHEN_VALID": False,
    "BLINK_STANDARD_ERROR": 0.57735027,
    "BLINK_FORWARD_POINTS": 15,
    "BLINK_MANA_THRESHOLD": 80,
    "BLINK_JUMP_DISTANCE": 0.056799,
    "JUMP_WHEN_VALID" : True,
    "JUMP_FORWARD_POINTS": 15,
    "JUMP_DISTANCE": 0.028799
}
paused = False
navigationActive = False


class WalkingControl:
    w = False
    s = False

    def startWalking(self):
        if not paused:
            if self.s:
                pyautogui.keyUp('s')
            if not self.w:
                pyautogui.keyDown('w')
            self.s = False
            self.w = True

    def startWalkingBackwads(self):
        if self.w:
            pyautogui.keyUp('w')
        if not self.s:
            pyautogui.keyDown('s')
        self.w = False
        self.s = True

    def stop(self):
        if self.w:
            pyautogui.keyUp('w')
        if self.s:
            pyautogui.keyUp('s')
        self.w = False
        self.s = False

class TurningControl:
    turnTimeout = None
    turnDone = False
    turnKey = None

    def TimerOver(self):
        self.turnDone = True


    def askTurn(self, time, key):
        if not paused:
            self.stop()
            self.turnDone = False
            self.turnTimeout = threading.Timer((time/1000), self.TimerOver)
            self.turnKey = key
            pyautogui.keyDown(self.turnKey)
            self.turnTimeout.start()
            while not self.turnDone:
                pass
            pyautogui.keyUp(self.turnKey)
            self.TurnDone = False

    def askTurnLeft(self, time):
        self.askTurn(time, 'a')

    def askTurnRight(self, time):
        self.askTurn(time, 'd')

    def stop(self):
        if self.turnTimeout:
            self.turnTimeout.cancel()
            pyautogui.keyUp(self.turnKey)

tc = TurningControl()
wc = WalkingControl()



def DegToRad(degrees):
    return degrees * math.pi / 180

def RadToDeg(radians):
    return radians * 180 / math.pi

def pointDistance(x1, y1, x2, y2):
    xDistSq = math.pow(x2 - x1, 2)
    yDistSq = math.pow(y2 - y1, 2)
    return math.sqrt(xDistSq + yDistSq)

def ComputeTurnDegree(playerX, playerY, targetX, targetY):
    new_facing_direction = math.atan2(targetY - playerY, playerX - targetX)
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
    return new_facing_direction

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


#Accuracy = 'fine' or 'rough'
def MoveTo(X, Y, accuracy, config=None):

    wc.startWalking()

    if config is None:
        config = default
    if accuracy == 'fine':
        distanceAccuracy = config["POINT_FINE_DISTANCE_ERROR"]
    else:
        distanceAccuracy = config["POINT_DISTANCE_ERROR"]
    if accuracy == 'fine':
        minTurnTime  = config["MINIMUM_TURN_TIME_MS"]/3
    else:
        minTurnTime  = config["MINIMUM_TURN_TIME_MS"]

    while True:
        while paused:
            wc.stop()
            tc.stop()

        if pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y) < distanceAccuracy:
            print("Found point!")
            return

        new_facing_direction = ComputeTurnDegree(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y)

        directionDiff = new_facing_direction - Data.PLAYER_FACING
        if (directionDiff > math.pi):
            directionDiff = ((math.pi * 2) - directionDiff) * -1
        if (directionDiff < -math.pi):
            directionDiff = (math.pi * 2) - (directionDiff * -1)

        turnTime = (RadToDeg(directionDiff) / 360) * config["TURN_TIME_FACTOR"]

        print("turntime is" + str(turnTime))

        if math.fabs(turnTime) > config["MINIMUM_CORRECTING_TURN_TIME_MS"]:
            print("Making a correcting turn")
            turnTime = (RadToDeg(directionDiff) / 360) * config["CORRECTING_TURN_TIME_FACTOR"]
            wc.stop()
            #print("stopwalking")
        else:
            #print("Startwalking")
            wc.startWalking()

        if math.fabs(turnTime) > minTurnTime:
            # If turnTime is positive, make left turn
            if turnTime > 0:
                tc.askTurnLeft(turnTime)
            #// If negative value, function makes a right turn
            elif turnTime < 0:
                #// Converts negative time into positive for setTimeout in turnRightWowFinish
                turnTime = math.fabs(turnTime)
                tc.askTurnRight(turnTime)


def FollowPath(threadname,  path):
    navigationActive = True

    closest_point =path[0]
    closest_point_dist = 100000000
    index = 0
    for i, (X,Y) in enumerate(path):
        if pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y) < closest_point_dist:
            closest_point = (X,Y)
            closest_point_dist = pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y)
            index = i

    for X,Y in path[index:]:
        while paused:
            pass
            #print("Movement paused, waiting....")
            wc.stop()
        MoveTo(X,Y, 'fine')

    while True:
        path.reverse()
        for X,Y in path:
            while paused:
                pass
                #print("Movement paused, waiting....")
                wc.stop()
            MoveTo(X,Y, 'fine')
    wc.stop()
    navigationActive = False

def recordMovement():
    f = open("path", "wb")
    movement_coords = []
    #record every 0.2sec
    same = False
    old_X = 0
    old_Y = 0
    while len(movement_coords) < 10000:
        old_X = Data.PLAYER_X_COORD
        old_Y = Data.PLAYER_Y_COORD
        time.sleep(0.5)
        movement_coords.append((Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD))
        print(str(Data.PLAYER_X_COORD) + "," + str(Data.PLAYER_Y_COORD))
        if old_X == Data.PLAYER_X_COORD and old_Y == Data.PLAYER_Y_COORD:
            if same == True:
                break
            same = True
        else:
            same = False

    pickle.dump(movement_coords, f)
    f.close()
    print("Done recording...")

def readPath():
    f = open("path", "rb")
    movement_coords = pickle.load(f)
    return movement_coords