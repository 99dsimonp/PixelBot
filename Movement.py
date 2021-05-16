import math
import Data
import time
import threading
import pickle
import Inputter
import Point
from threading import Thread
import PixelReader as PR

default = {
    "NEAREST_POINT_THRESHOLD": 0.3,
    "NAVIGATION_FUNCTION_INTERVAL": 10,
    "POINT_DISTANCE_ERROR": 0.007,
    "POINT_FINE_DISTANCE_ERROR": 0.003,
    "TURN_TIME_FACTOR": 878.333333,
    "CORRECTING_TURN_TIME_FACTOR": 2000, #was 400, takes 2 sec for full turn
    "MINIMUM_CORRECTING_TURN_TIME_MS": 300, #Was 200
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
inp = Inputter.Inputter("World of Warcraft")


class WalkingControl:
    w = False
    s = False

    def startWalking(self):
        if not paused:
            if self.s:
                inp.keyup('s')
                #pyautogui.keyUp('s')
            if not self.w:
                inp.keydown('w')
                #pyautogui.keyDown('w')
            self.s = False
            self.w = True

    def startWalkingBackwads(self):
        if self.w:
            inp.keyup('w')
            #pyautogui.keyUp('w')
        if not self.s:
            inp.keydown('s')
            #pyautogui.keyDown('s')
        self.w = False
        self.s = True

    def stop(self):
        if self.w:
            inp.keyup('w')
            #pyautogui.keyUp('w')
        if self.s:
            inp.keyup('s')
            #pyautogui.keyUp('s')
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
            print("Turning for " + str(time) + "ms" )
            self.stop()
            self.turnDone = False
            self.turnTimeout = threading.Timer((time/1000), self.TimerOver)
            self.turnKey = key
            inp.keydown(self.turnKey)
            #pyautogui.keyDown(self.turnKey)
            self.turnTimeout.start()
            while not self.turnDone:
                pass
            inp.keyup(self.turnKey)
            #pyautogui.keyUp(self.turnKey)
            self.TurnDone = False

    def askTurnLeft(self, time):
        self.askTurn(time, 'a')

    def askTurnRight(self, time):
        self.askTurn(time, 'd')

    def stop(self):
        if self.turnTimeout:
            self.turnTimeout.cancel()
            inp.keyup(self.turnKey)
            #pyautogui.keyUp(self.turnKey)

class Path:
    p = []
    curr_ix = 0
    dir_forward = False

    def FindClosestPoint(self):
        closest_point_dist = 100000000
        for i, (X,Y) in enumerate(self.p):
            dist = pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y)
            if dist < closest_point_dist:
                closest_point_dist = dist
                self.curr_ix = i
        return

    def __init__(self, p):
        self.p = p

    def Next(self):
        current_point = self.p[self.curr_ix]
        if self.curr_ix == len(self.p) - 1:
            self.curr_ix -= 1
            self.dir_forward = False
        if self.curr_ix == 0:
            self.dir_forward = True
            self.curr_ix += 1
        if self.dir_forward:
            self.curr_ix += 1
        if not self.dir_forward:
            self.curr_ix -= 1
        #print("Next point is: " + str(self.curr_ix))

        if pointDistance(*current_point, *self.p[self.curr_ix]) > 0.6:
            print("Next point seems to be erroneous:" + str(pointDistance(*current_point, *self.p[self.curr_ix])))
            return self.Next()
        return self.p[self.curr_ix]



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


# Calculate the distance between two points (using distance formula)
def get_distance_off_tow_pos(p1: Point, p2: Point):
    return round(((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5, 8)


# Calculate the angle based on the three-point coordinates (steering angle)
# a is the starting point and the side of the current point
# b is the side from the starting point to the target point
# c is the side from the current point to the target point
# Set: S is the starting point, N is the current point, and T is the target point
# First use the Pythagorean theorem to calculate the length of the three sides of the triangle, and then use the arc cosine to calculate the radian and angle
# The angle is the number of angles ab + the number of angles bc
def posToDegree(startPos: Point, nowPos: Point, targetPos: Point):
    a = get_distance_off_tow_pos(startPos, nowPos)
    b = get_distance_off_tow_pos(startPos, targetPos)
    c = get_distance_off_tow_pos(nowPos, targetPos)
    print("a = " + str(a) + ", b = " + str(b) + ", c = " + str(c))

    if a == 0:  # The terrain may be stuck at 0
        return 9999
    if b == 0:
        print("The starting point and the target point coincide")
        return 0
    if c == 0:
        print("The current point and the target point coincide")
        return 0

    # The parameter value of the arc cosine must be in the range of [-1,1].
    # Because the calculation error of the floating point number of the computer
    # may be greater than 1 or less than -1, it must be compatible here.
    tmp = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
    tmp = 1 if tmp >= 1 else tmp
    tmp = -1 if tmp <= -1 else tmp
    degreeNST = math.degrees(math.acos(tmp))  # Angle NST in degrees

    tmp = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
    tmp = 1 if tmp >= 1 else tmp
    tmp = -1 if tmp <= -1 else tmp
    degreeNTS = math.degrees(math.acos(tmp))  # Angle NTS degrees

    degree = degreeNST + degreeNTS
    #The actual angle to be corrected should be the supplementary angle of the angle SNT, that is, the sum of the other two internal angles of the triangle
    print("angle = " + str(degree))
    return degree


# Calculate the radian difference from the current point to the target point
def calNowToTargetFacing(nowPos: Point, targetPos: Point):
    slope = math.atan2(targetPos.y - nowPos.y, nowPos.x - targetPos.x)  # Arctangent calculates the azimuth in radians, that is, the angle with the x-axis
    print("Arctangent：" + str(slope))
    slope = slope + math.pi  #Because the arctangent function value range is (-π/2,π/2), it needs to be converted to the range of 0-2π
    slope = slope - math.pi * 0.5  # This radian is the absolute radian from the current point to the target point, which needs to be converted into wow radian, rotated 90° left. Make up (north) 0, not right, consistent with wow
    if slope < 0:
        slope = slope + math.pi * 2  #Make sure radians are not a negative number

    if slope > math.pi * 2:  # Also make sure that the radian does not exceed 2π
        slope = slope - math.pi * 2
    print("Value after arctangent value processing：" + str(slope))
    return slope

def leftOrRightByFacing(playerFacing, nowPos: Point, targetPos: Point):
    slope = calNowToTargetFacing(nowPos, targetPos)
    directionDiff = slope - playerFacing  #The difference between the radian of the target point and the current radian
    print("Radian difference：" + str(directionDiff))
    if directionDiff > math.pi:
        directionDiff = ((math.pi * 2) - directionDiff) * -1 #If greater than 180°, take another angle, namely 360°-directionDiff, and take the negative
    if directionDiff < -math.pi:
        directionDiff = (math.pi * 2) - (directionDiff * -1)  #Less than minus 180° actually has the same meaning as greater than 180°. It also takes an angle and takes positive

    print("Radian difference after processing：" + str(directionDiff))
    if directionDiff > 0:
        return "left"
    return "right"

# Calculate the steering time (amplitude) according to the angle, test 0.52 seconds about 90 degrees
def degreeToTime(self, degree):
    one_degree_time = 0.50 / 90  # How many seconds does it take to turn 1 degree
    return one_degree_time * degree


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

    prev_error = 100000.0

    while True:
        while paused:
            wc.stop()
            tc.stop()
            return

        print("Dist to target point: " + str(pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y)))
        if prev_error < pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y):
            print("Prev error: " + str(prev_error) + " Curr error: " + str(pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y)))

        if pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y) < distanceAccuracy:
            #print("Found point!")
            return
        prev_error = pointDistance(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y)

        new_facing_direction = ComputeTurnDegree(Data.PLAYER_X_COORD, Data.PLAYER_Y_COORD, X, Y)

        directionDiff = new_facing_direction - Data.PLAYER_FACING
        if (directionDiff > math.pi):
            directionDiff = ((math.pi * 2) - directionDiff) * -1
        if (directionDiff < -math.pi):
            directionDiff = (math.pi * 2) - (directionDiff * -1)

        turnTime = (RadToDeg(directionDiff) / 360) * config["TURN_TIME_FACTOR"]

        #print("turntime is" + str(turnTime))

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




def FollowPath(threadname,  inputpath):
    p = Path(inputpath)
    p.FindClosestPoint()

    recently_paused = False

    while True:
        while paused:
            wc.stop()
            recently_paused = True
        if recently_paused:
            p.FindClosestPoint()
        next = p.Next()
        MoveTo(*next, 'fine')

    wc.stop()

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
            # If we already have two points that are identical
            if same:
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

if __name__ == "__main__":
    thread1 = Thread(target=PR.thread_monitor, args=("Thread-1",))
    thread1.start()
    time.sleep(1)
    recordMovement()
