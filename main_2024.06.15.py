import pygame
import random
import math
import time
from PIL import Image  # Used to get width and height of the window

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 153, 255)
PLAYER1_COL = (255, 87, 12)  # Used for player 1 progress bar
PLAYER2_COL = (0, 169, 252)  # Used for player 2 progress bar

# Constants
TRACK_NUM = 2  # 1 or 2
FPS = 30  # Frame rate of the game (frames per second)
N_STARS = 1000
N_VEHICLES = 5  # Number of vehicles per player
COUNTDOWN = 3  # Used for 3... 2... 1... counter
RACE_DURATION = 60  # Race duration (s)
PROGRESS_BAR_SIZE = [300, 10]  # Width x height (px) of progress bars
TOP_BANNER_HEIGHT = 55  # Height of the top banner
EPSILON = 1e-5  # Used to clean up the race countdown
VEHICLE_WIDTH = 80  # Width of each vehicle (px)
VESSEL_WIDTH = 100  # Width of each vessel (px)
FRUIT_WIDTH = 50  # Width of each fruit (px)
STAR_BASE_COLOR = pygame.color.Color(PINK)
STAR_BASE_COLOR_H, STAR_BASE_COLOR_S, STAR_BASE_COLOR_V, STAR_BASE_COLOR_A = STAR_BASE_COLOR.hsva  # Used to define stars
WORLD_SIZE = 1000  # Used to define stars
DISTANCE_TO_VIEWING_PLANE = 200  # Used to define stars
STAR_SIZE = 2  # Used to define stars
STAR_SPEED = 1  # Used to define stars
STAR_ANGLE = -0.0016  # Used to define stars
DISPLAY_DEBUG = 0  # Used to determine if debug data shall be displayed on the screen

# Vehicle definition
VEHICLE_FILENAMES = ['Rocket01.png', 'Rocket02.png']  # 'Circle_red.png'

# 0: Average vehicle speed (px/frame)
# 1: Probability that a vehicle will change its speed on the track
# 2: Minimum value of speed ratio
# 3: Maximum value of speed ratio
# 4: Minimum absolute value of the acceleration ratio
# 5: Maximum absolute value of the acceleration ratio
# VEHICLE_SPEED_PARAMS = [6, 0.00, 0.6, 1.4, 0.01, 0.03]
VEHICLE_SPEED_PARAMS = [6, 0.02, 0.6, 1.4, 0.01, 0.03]

# 0: Maximum absolute value of vehicle lateral position (lat)
# 1: Probability that a vehicle will change its lateral position along the width of the track
# 2: Minimum absolute value of the lateral speed ratio
# 3: Maximum absolute value of the lateral speed ratio
# VEHICLE_LAT_PARAMS = [0.5, 0.00, 0.01, 0.03]
VEHICLE_LAT_PARAMS = [0.5, 0.08, 0.01, 0.03]

# Vessel definition
VESSEL_FILENAMES = ['Vessel01.png', 'Vessel02.png']

# 0: Initial position of the first vessel along x (in % of the window width)
# 1: Initial position of the first vessel along y (in % of the window height)
# 2: Vessel speed (px/frame)
VESSEL_PARAMS = [0.4, 0.38, 5]

# Fruit definition
FRUIT_FILENAMES = ['Fruit01.png']

# 0: Fruit linear speed (px/frame)
# 1: Fruit rotation speed (rad/frame)
# 2: Latency allowed between 2 shots (s)
FRUIT_PARAMS = [10, 0.15, 1]

# 0: 'Up' key
# 1: 'Down' key
# 2: 'Left' key
# 3: 'Right' key
# 4: 'Shoot' key
VESSEL_KEYS = [
    [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_x],
    [pygame.K_o, pygame.K_l, pygame.K_k, pygame.K_SEMICOLON, pygame.K_PERIOD]
]

# Track definition
if TRACK_NUM == 1:  # Track #1
    TRACK_FILENAME = 'Track01.png'
    TRACK_SEG_TYPES = [1, 2, 1, 2]  # Segment types: 1 = straight lines, 2 = arc (1st segment shall be a straight line)
    TRACK_TRANS_POINTS = [
        [350.0, 200.0, 75.0],
        [830.0, 200.0, 125.0],
        [776.6, 541.7, 125.0],
        [319.5, 395.2, 75.0]
    ]  # Track transition points: (x, y) coordinates, and track width
    TRACK_NSEG = len(TRACK_TRANS_POINTS)  # Number of segments - 1
    TRACK_ARC_DATA = [
        [0.0, 0.0, 0.0],
        [830.0, 375.0, 175.0],
        [0.0, 0.0, 0.0],
        [350.0, 300.0, 100.0]
    ]  # Center points and radius of curvature for arc segments: (x, y, R)
    TRACK_ANGLES = [0.000, 0.000, -2.831, -2.831]  # Start angles for each segment (rad)
    TRACK_ARC_ORIENT = [0, 1, 0, 1]  # Orientation of arc segments: +1 if CCW, -1 if CW
    TRACK_KSI = 0.5  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
    TRACK_STARTING_GRID = [3, 1.00, 0.10, 0.10]  # Number of vehicles next to one another on starting grid, lateral spacing between all vehicles, ksi offset behind finish line for first vehicle, and ksi value between each vehicle

elif TRACK_NUM == 2:  # Track #2
    TRACK_FILENAME = 'Track02.png'
    TRACK_SEG_TYPES = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]  # Segment types: 1 = straight lines, 2 = arc (1st segment shall be a straight line)
    TRACK_TRANS_POINTS = [
        [237.6, 125.0, 125.0],
        [1065.0, 125.0, 125.0],
        [1130.0, 190.0, 125.0],
        [1130.0, 208.0, 125.0],
        [1065.0, 273.0, 125.0],
        [874.5, 273.0, 125.0],
        [809.5, 338.0, 125.0],
        [809.5, 392.5, 125.0],
        [874.5, 457.5, 125.0],
        [1025.0, 457.5, 125.0],
        [1090.0, 522.5, 125.0],
        [1090.0, 529.0, 125.0],
        [1025.0, 594.0, 125.0],
        [697.0, 594.0, 125.0],
        [632.0, 529.0, 125.0],
        [632.0, 467.5, 125.0],
        [567.0, 402.5, 125.0],
        [493.5, 402.5, 125.0],
        [428.5, 467.5, 125.0],
        [428.5, 529.0, 125.0],
        [363.5, 594.0, 125.0],
        [332.6, 594.0, 125.0],
        [270.0, 546.5, 125.0],
        [175.0, 207.5, 200.0]
    ]  # Track transition points: (x, y) coordinates, and track width
    TRACK_NSEG = len(TRACK_TRANS_POINTS)  # Number of segments - 1
    TRACK_ARC_DATA = [
        [0.0, 0.0, 0.0],
        [1065.0, 190.0, 65.0],
        [0.0, 0.0, 0.0],
        [1065.0, 208.0, 65.0],
        [0.0, 0.0, 0.0],
        [874.5, 338.0, 65.0],
        [0.0, 0.0, 0.0],
        [874.5, 392.5, 65.0],
        [0.0, 0.0, 0.0],
        [1025.0, 522.5, 65.0],
        [0.0, 0.0, 0.0],
        [1025.0, 529.0, 65.0],
        [0.0, 0.0, 0.0],
        [697.0, 529.0, 65.0],
        [0.0, 0.0, 0.0],
        [567.0, 467.5, 65.0],
        [0.0, 0.0, 0.0],
        [493.5, 467.5, 65.0],
        [0.0, 0.0, 0.0],
        [363.5, 529.0, 65.0],
        [0.0, 0.0, 0.0],
        [332.6, 529.0, 65.0],
        [0.0, 0.0, 0.0],
        [237.6, 190.0, 65.0]
    ]  # Center points and radius of curvature for arc segments: (x, y, R)
    TRACK_ANGLES = [0.000, 0.000, 1.571, 1.571, 3.142, 3.142, 1.571, 1.571, 0.000, 0.000, 1.571, 1.571, 3.142, 3.142, -1.571, -1.571, 3.142, 3.142, 1.571, 1.571, 3.142, 3.142, -1.845, -1.845]  # Start angles for each segment (rad)
    TRACK_ARC_ORIENT = [0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1]  # Orientation of arc segments: +1 if CCW, -1 if CW when y-axis is pointing upward
    TRACK_KSI = 0.77  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
    TRACK_STARTING_GRID = [3, 0.07, 0.07]  # Number of vehicles next to one another on starting grid, ksi offset behind finish line for first vehicle, and ksi value between each vehicle
    # TRACK_STARTING_GRID = [3, 0.07, 0.00]

TRACK_IMG = Image.open(TRACK_FILENAME)
WINDOW_WIDTH = TRACK_IMG.width  # 1280
WINDOW_HEIGHT = TRACK_IMG.height  # 720

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display_font_1 = pygame.font.SysFont('times new roman', 12)
display_font_2 = pygame.font.SysFont('times new roman', 75, bold = True)
display_font_3 = pygame.font.SysFont('times new roman', 50, bold = True)
display_font_4 = pygame.font.SysFont('times new roman', 20, bold = True)
clock = pygame.time.Clock()

background = pygame.image.load(TRACK_FILENAME)


class Track():
    def __init__(self):
        self.segTypes = []
        self.transPoints = [[]]  # Track transition points: (x, y) coordinates, and track width
        self.nSeg = 0  # Number of segments
        self.arcData = [[]]  # Center points and radius of curvature for arc segments: (x, y, R)
        self.angles = []  # Start angles for each segment (rad)
        self.arcOrient = []  # Orientation of arc segments: +1 if CCW, -1 if CW
        self.startKsi = 0.0  # ksi at start/finish line (on first segment, assumed straight)
        self.segLen = []  # Length of each segment
        self.trackLen = 0  # Length of the entire track
        self.maxRaceLength = 0  # Maximum race length (number of laps)

    def __init__(self, segTypes, transPoints, arcData, angles, arcOrient, startKsi):
        self.segTypes = segTypes  # Segment types: 1 = straight lines, 2 = arc
        self.transPoints = transPoints  # Track transition points: (x, y) coordinates, and track width
        self.nSeg = len(transPoints)  # Number of segments
        self.arcData = arcData  # Center points and radius of curvature for arc segments: (x, y, R)
        self.angles = angles  # Start angles for each segment (rad)
        self.arcOrient = arcOrient  # Orientation of arc segments: +1 if CCW, -1 if CW
        self.startKsi = startKsi  # ksi at start/finish line (on first segment, assumed straight)
        self.segLen = []  # Length of each segment
        self.trackLen = 0  # Length of the entire track
        for seg in range(self.nSeg):
            segPlusOne = (seg + 1) % self.nSeg
            if self.segTypes[seg] == 1:  # If the segment is a straight line
                segLen = math.sqrt((self.transPoints[segPlusOne][0] - self.transPoints[seg][0]) ** 2 + (self.transPoints[segPlusOne][1] - self.transPoints[seg][1]) ** 2)  # Length of current segment: L = sqrt(x^2 + y^2)
                self.segLen.append(segLen)
            else:  # If the segment is an arc
                dTheta = self.angles[segPlusOne] - self.angles[seg]
                if (self.arcOrient[seg] == 1 and dTheta < 0):  # If the segment is CCW and the end angle is smaller than the start angle
                    dTheta += 2 * math.pi
                if (self.arcOrient[seg] == -1 and dTheta > 0):  # If the segment is CW and the end angle is larger than the start angle
                    dTheta -= 2 * math.pi
                segLen = self.arcData[seg][2] * abs(dTheta)  # Length of current segment: L = R * theta
                self.segLen.append(segLen)
            self.trackLen += segLen  # Update track total length
        self.maxRaceLength = RACE_DURATION * FPS * VEHICLE_SPEED_PARAMS[0] * VEHICLE_SPEED_PARAMS[3] / self.trackLen  # Maximum race length (number of laps)


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, vehicleFilename, playerNum, ksi, lat, speedUpdate):
        super().__init__()
        self.playerNum = playerNum
        self.imageInit = pygame.image.load(vehicleFilename).convert_alpha()
        imgSize = self.imageInit.get_size()
        self.imageInit = pygame.transform.scale(self.imageInit, (int(VEHICLE_WIDTH), int(VEHICLE_WIDTH * imgSize[1] / imgSize[0])))

        self.image = pygame.transform.rotate(self.imageInit, track1.angles[0]*180/math.pi)
        self.rect = self.image.get_rect()
        self.seg = 0  # Starts at segment 0
        self.ksi = ksi  # Vehicle position at the start/finish line
        self.lat = lat  # Vehicle lateral position at the start/finish line
        self.latUpdate = [0, 0, 0, 0]  # Is the lateral position currently being updated? If yes: start position, end position, acceleration ratio
        self.speed = 0  # Vehicle speed (starts at rest on the starting grid)
        self.speedUpdate = speedUpdate # [x, x, x, x, x] - 0. Is the speed currently being updated? If yes: 1. start speed, 2. end speed, 3. acceleration ratio. 4. Is the vehicle being forced to stop?
        vehicleCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
        self.rect.center = (vehicleCoords[0], vehicleCoords[1])  # Initial position of the vehicle
        self.dir = vehicleCoords[2]  # Initial direction of the vehicle (rad)
        self.lap = 0  # Lap number
        self.distance = 0  # Distance covered by the vehicle

    def update(self):
        # Update speed
        if self.speedUpdate[4] == 0:  # If the vehicle is not being forced to stop
            if self.speedUpdate[0] == 0:  # If the speed is currently not being updated
                if random.random() < VEHICLE_SPEED_PARAMS[1]:
                    startSpeed = self.speed  # Start speed
                    endSpeed = random.uniform(VEHICLE_SPEED_PARAMS[2], VEHICLE_SPEED_PARAMS[3]) * VEHICLE_SPEED_PARAMS[0]  # Pick end speed
                    accelRatio = random.uniform(VEHICLE_SPEED_PARAMS[4], VEHICLE_SPEED_PARAMS[5])  # Acceleration (or deceleration)
                    self.speedUpdate = [1, startSpeed, endSpeed, accelRatio, 0]
            if self.speedUpdate[0] == 1:  # If the speed is currently being updated
                self.speed += self.speedUpdate[3]*(self.speedUpdate[2] - self.speedUpdate[1])
                if ((self.speedUpdate[2] - self.speedUpdate[1] >= 0) and (self.speed >= self.speedUpdate[2])) or ((self.speedUpdate[2] - self.speedUpdate[1] < 0) and (self.speed <= self.speedUpdate[2])):  # If the speed has reached its to-be-updated-to value
                    self.speed = self.speedUpdate[2]
                    self.speedUpdate = [0, 0, 0, 0, 0]
        else:  # If the vehicle is being forced to stop
            self.speed += self.speedUpdate[3] * (self.speedUpdate[2] - self.speedUpdate[1])
            if self.speed <= self.speedUpdate[2]:  # If the speed has reached 0
                self.speed = 0.0

        # Update lateral position
        if self.speedUpdate[4] == 0:  # If the vehicle is not being forced to stop
            if self.latUpdate[0] == 0:  # If the lateral position is currently not being updated
                if random.random() < VEHICLE_LAT_PARAMS[1]:
                    startLat = self.lat  # Start lateral position
                    endLat = random.uniform(-VEHICLE_LAT_PARAMS[0], VEHICLE_LAT_PARAMS[0])  # Pick end lateral position
                    accelRatio = random.uniform(VEHICLE_LAT_PARAMS[2], VEHICLE_LAT_PARAMS[3])  # Acceleration (or deceleration)
                    self.latUpdate = [1, startLat, endLat, accelRatio]
            if self.latUpdate[0] == 1:  # If the lateral position is currently being updated
                self.lat += self.latUpdate[3]*(self.latUpdate[2] - self.latUpdate[1])
                if ((self.latUpdate[2] - self.latUpdate[1] >= 0) and (self.lat >= self.latUpdate[2]) or (self.latUpdate[2] - self.latUpdate[1] < 0) and (self.lat <= self.latUpdate[2])):
                    self.lat = self.latUpdate[2]
                    self.latUpdate = [0, 0, 0, 0]

        # Update position on the track
        distanceToCover = self.speed  # Distance by which the vehicle needs to move in the time increment
        if track1.segTypes[self.seg] == 2:  # Adjust distanceToCover to take vehicle's lateral position into account, if the segment is an arc:
            segPlusOne = (self.seg + 1) % track1.nSeg  # Index of next segment
            trackWidth = track1.transPoints[self.seg][2] + ksi * (track1.transPoints[segPlusOne][2] - track1.transPoints[self.seg][2])  # Track width
            distanceToCover = distanceToCover * track1.arcData[self.seg][2] / (track1.arcData[self.seg][2] - track1.arcOrient[self.seg] * self.lat * trackWidth / 2)
        while distanceToCover > 0:
            newKsi = self.ksi + distanceToCover / track1.segLen[self.seg]
            if newKsi < 1:  # If the vehicle is still in the same segment
                if (self.seg == 0 and self.ksi < track1.startKsi and newKsi >= track1.startKsi):  # Update lap number
                    self.lap += 1
                self.ksi = newKsi
                newCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
                self.dir = newCoords[2]
                self.image = pygame.transform.rotate(self.imageInit, -self.dir * 180 / math.pi) # Orient the vehicle according to the local orientation of the track
                self.rect = self.image.get_rect()
                self.rect.center = (newCoords[0], newCoords[1])
                distanceToCover = 0
            else:  # If the vehicle is now in the next segment
                distanceToCover -= track1.segLen[self.seg] * (1 - self.ksi)
                self.seg = (self.seg + 1) % track1.nSeg  # Move to the next segment
                self.ksi = 0.0

        # Calculate distance covered by vehicle (updated only once the vehicle has crossed the start line for the first time, and only if the vehicle is not being forced to stop once the race timer has timed out)
        if self.lap >= 1 and self.speedUpdate[4] == 0:
            self.distance = (self.lap - 1) * track1.trackLen - TRACK_KSI * track1.segLen[0] + self.ksi * track1.segLen[self.seg]
            for iSeg in range(self.seg):
                self.distance += track1.segLen[iSeg]
            if self.seg == 0 and self.ksi < TRACK_KSI:
                self.distance += track1.trackLen


class Vessel(pygame.sprite.Sprite):
    def __init__(self, vesselFilename, playerNum, initPosition):
        super().__init__()
        self.playerNum = playerNum
        self.dir = math.pi/2  # Direction w.r.t. horizontal (rad)
        self.imageInit = pygame.image.load(vesselFilename).convert_alpha()
        imgSize = self.imageInit.get_size()
        self.image = pygame.transform.scale(self.imageInit, (int(VESSEL_WIDTH), int(VESSEL_WIDTH * imgSize[1] / imgSize[0])))
        self.rect = self.image.get_rect()
        self.rect.center = initPosition  # Initial position of the vehicle
        self.lastShotTime = 0  # Time of the last projectile shot

    def update(self):
        # Update vessel position
        keys = pygame.key.get_pressed()
        if keys[VESSEL_KEYS[self.playerNum][0]] and self.rect.y > TOP_BANNER_HEIGHT:
            self.rect.y -= VESSEL_PARAMS[2]  # move up
            self.dir = math.pi/2
        if keys[VESSEL_KEYS[self.playerNum][1]] and self.rect.y < WINDOW_HEIGHT - self.rect.height:
            self.rect.y += VESSEL_PARAMS[2]  # move down
            self.dir = -math.pi / 2
        if keys[VESSEL_KEYS[self.playerNum][2]] and self.rect.x > 0:
            self.rect.x -= VESSEL_PARAMS[2]  # move left
            self.dir = math.pi
        if keys[VESSEL_KEYS[self.playerNum][3]] and self.rect.x < WINDOW_WIDTH - self.rect.width:
            self.rect.x += VESSEL_PARAMS[2]  # move right
            self.dir = 0

        # Shoot fruit
        if keys[VESSEL_KEYS[self.playerNum][4]] and time.time() - self.lastShotTime > FRUIT_PARAMS[2]:
            self.lastShotTime = time.time()
            fruit = Fruit(self.rect.center, self.dir, 0)
            allProjectileSprites.add(fruit)


class Fruit(pygame.sprite.Sprite):
    def __init__(self, initPosition, initDir, type):
        super().__init__()
        self.type = type  # Type of fruit
        self.dir = initDir  # Direction in which the fruit is moving
        self.angle = 0  # Orientation of the fruit (rad)
        self.imageInit = pygame.image.load(FRUIT_FILENAMES[self.type]).convert_alpha()
        imgSize = self.imageInit.get_size()
        self.imageInit = pygame.transform.scale(self.imageInit, (int(FRUIT_WIDTH), int(FRUIT_WIDTH * imgSize[1] / imgSize[0])))
        self.image = pygame.transform.rotate(self.imageInit, self.angle * 180 / math.pi)
        self.rect = self.image.get_rect()
        self.rect.center = initPosition  # Initial position of the fruit

    def update(self):
        # Update fruit position and orientation
        if -self.rect.width < self.rect.x < WINDOW_WIDTH and TOP_BANNER_HEIGHT < self.rect.y < WINDOW_HEIGHT:
            self.angle += FRUIT_PARAMS[1]
            newCoords = [self.rect.centerx + FRUIT_PARAMS[0] * math.cos(self.dir), self.rect.centery - FRUIT_PARAMS[0] * math.sin(self.dir)]
            self.image = pygame.transform.rotate(self.imageInit, -self.angle * 180 / math.pi)
            self.rect = self.image.get_rect()
            self.rect.center = (newCoords[0], newCoords[1])
        else:  # Destroy the fruit if it reaches the edges of the window
            self.kill()


class Player():
    def __init__(self, playerNum, vehicleGroup, vessel):
        self.playerNum = playerNum
        self.vehicleGroup = vehicleGroup
        self.score = 0.00  # Score (out of 100)
        self.vessel = vessel

    # Update the score of a player
    def updateScore(self):
        self.score = 0.00
        for vehicle in self.vehicleGroup:
            self.score += vehicle.distance / track1.trackLen
        self.score = self.score / N_VEHICLES

class Star():
    def __init__(self):
        self.x = random.randint(-WORLD_SIZE, WORLD_SIZE)
        self.y = random.randint(-WORLD_SIZE, WORLD_SIZE)
        self.z = random.randint(1, WORLD_SIZE)

    def perspectiveTransform(self):
        x_plane = WINDOW_WIDTH // 2 if self.z * self.x == 0 else DISTANCE_TO_VIEWING_PLANE / self.z * self.x + WINDOW_WIDTH // 2
        y_plane = WINDOW_HEIGHT // 2 if self.z * self.y == 0 else DISTANCE_TO_VIEWING_PLANE / self.z * self.y + WINDOW_HEIGHT // 2
        return x_plane, y_plane

    def rotation(self, angle):
        x1 = self.x * math.cos(angle) - self.y * math.sin(angle)
        y1 = self.x * math.sin(angle) + self.y * math.cos(angle)
        return x1, y1

    def update(self):
        self.x, self.y = self.rotation(STAR_ANGLE)
        self.z -= STAR_SPEED
        if self.z < 1:
            self.z = WORLD_SIZE
        if self.z > WORLD_SIZE:
            self.z = 1

    def draw(self, window):
        v = 100 * (1 - (self.z / WORLD_SIZE))
        v = 100 if v > 100 else v
        v = 0 if v < 0 else v
        color = pygame.color.Color(BLACK)
        color.hsva = STAR_BASE_COLOR_H, STAR_BASE_COLOR_S, v, STAR_BASE_COLOR_A
        star_screen_x, star_screen_y = self.perspectiveTransform()
        pygame.draw.circle(window, color, (int(star_screen_x), int(star_screen_y)), STAR_SIZE)


def natToGlobal(track, seg, ksi, lat):  # Calculates global coords (x, y, theta) from natural coords (seg, ksi, lat)
    segPlusOne = (seg + 1) % track.nSeg  # Index of next segment
    trackWidth = track.transPoints[seg][2] + ksi * (track.transPoints[segPlusOne][2] - track.transPoints[seg][2])  # Track width
    if track.segTypes[seg] == 1:  # If the segment is a straight line
        theta = track.angles[seg]
        x = track.transPoints[seg][0] + ksi * (track.transPoints[segPlusOne][0] - track.transPoints[seg][0]) - lat * trackWidth/2 * math.sin(theta)
        y = track.transPoints[seg][1] + ksi * (track.transPoints[segPlusOne][1] - track.transPoints[seg][1]) + lat * trackWidth/2 * math.cos(theta)
    else:  # If the segment is an arc
        startAngle = track.angles[seg]
        endAngle = track.angles[segPlusOne]
        if track.arcOrient[seg] == 1:
            if endAngle < startAngle:  # If the segment is CCW and the end angle is smaller than the start angle
                endAngle += 2 * math.pi
            theta = startAngle + ksi * (endAngle - startAngle)
            x = track.arcData[seg][0] + track.arcData[seg][2] * math.cos(theta - math.pi / 2) - lat * trackWidth/2 * math.sin(theta)
            y = track.arcData[seg][1] + track.arcData[seg][2] * math.sin(theta - math.pi / 2) + lat * trackWidth/2 * math.cos(theta)
        if track.arcOrient[seg] == -1:
            if endAngle > startAngle:  # If the segment is CW and the end angle is larger than the start angle
                endAngle -= 2 * math.pi
            theta = startAngle + ksi * (endAngle - startAngle)
            x = track.arcData[seg][0] + track.arcData[seg][2] * math.cos(theta + math.pi / 2) - lat * trackWidth/2 * math.sin(theta)
            y = track.arcData[seg][1] + track.arcData[seg][2] * math.sin(theta + math.pi / 2) + lat * trackWidth/2 * math.cos(theta)
    return [x, y, theta]

# Create groups of sprites
allVehicleSprites = pygame.sprite.Group()  # All vehicle and vessel sprites
allProjectileSprites = pygame.sprite.Group()  # All projectile sprites

# Create vessels and players
players = []  # List of all players
for playerNum in range(2):
    vessel = Vessel(VESSEL_FILENAMES[playerNum], playerNum, [WINDOW_WIDTH * ((1 - playerNum) * VESSEL_PARAMS[0] + playerNum * (1 - VESSEL_PARAMS[0])), WINDOW_HEIGHT * VESSEL_PARAMS[1]])
    player = Player(playerNum, pygame.sprite.Group(), vessel)
    players.append(player)

# Create the track
track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)

# Create vehicles for each player and add to groups
playerNum = random.randint(0, 1)  # Randomly picks player in first place on starting grid
ksi = track1.startKsi - TRACK_STARTING_GRID[1]
if TRACK_STARTING_GRID[0] == 1:  # If only one row of vehicles
    lat = 0
else:
    lat = -VEHICLE_LAT_PARAMS[0]
i_lat = 1  # Index for lateral position
speedUpdate = [1, 0.00, VEHICLE_SPEED_PARAMS[0], VEHICLE_SPEED_PARAMS[5], 0] # Makes the vehicle accelerate to target speed from 0 speed
for i in range(2 * N_VEHICLES):
    vehicle = Vehicle(VEHICLE_FILENAMES[playerNum], playerNum, ksi, lat, speedUpdate)
    players[playerNum].vehicleGroup.add(vehicle)  # Add vehicle to vehicle group of appropriate player
    allVehicleSprites.add(vehicle)  # Add vehicle to group of all vehicle sprites
    ksi -= TRACK_STARTING_GRID[2]
    if TRACK_STARTING_GRID[0] == 1:  # If only one row of vehicles
        lat = 0
    else:
        i_lat = i_lat % TRACK_STARTING_GRID[0] + 1
        lat = -VEHICLE_LAT_PARAMS[0] + 2 * (i_lat - 1)/(TRACK_STARTING_GRID[0] - 1) * VEHICLE_LAT_PARAMS[0]
    playerNum = 1 - playerNum  # Switch player

# Add vessels to allVehicleSprites after vehicles have already been added, so they appear on top
for player in players:
    allVehicleSprites.add(player.vessel)  # Add vessel to group of all vehicle sprites

# Define stars
stars = []
for i in range(N_STARS):
    stars.append(Star())

# Main loop
phase = 1  # 1:  3... 2... 1... countdown phase; 2: game phase; 3: post-game phase
running = True

progress_bar1 = pygame.Surface(PROGRESS_BAR_SIZE)
progress_bar1.fill(GRAY)
progress_bar_im1 = pygame.Surface((1, PROGRESS_BAR_SIZE[1]))
progress_bar_im1.fill(PLAYER1_COL)
progress_bar_pos1 = pygame.Vector2()
progress_bar2 = pygame.Surface(PROGRESS_BAR_SIZE)
progress_bar2.fill(GRAY)
progress_bar_im2 = pygame.Surface((1, PROGRESS_BAR_SIZE[1]))
progress_bar_im2.fill(PLAYER2_COL)
progress_bar_pos2 = pygame.Vector2()

startTime = time.time()
currentTime = time.time()
while running:
    pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    window.blit(background, background.get_rect())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and draw stars
    for star in stars:
        star.update()
        star.draw(window)

    if phase == 1:  # 3... 2... 1... countdown phase
        # Display 3... 2... 1... countdown
        countdown = display_font_2.render(str(int(COUNTDOWN + startTime - currentTime + 1)) + '...', True, WHITE)
        text_rect = countdown.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
        window.blit(countdown, text_rect)
    elif phase == 2:  # Race phase
        pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BANNER_HEIGHT))
        # Display race timer
        raceTimer = display_font_3.render(str(int(RACE_DURATION + startTime - currentTime)), True, YELLOW)
        text_rect = raceTimer.get_rect(center=(WINDOW_WIDTH / 2, 30))
        window.blit(raceTimer, text_rect)
    elif phase == 3:  # Post-game phase
        pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BANNER_HEIGHT))
        raceTimer = display_font_3.render('0', True, YELLOW)
        text_rect = raceTimer.get_rect(center=(WINDOW_WIDTH / 2, 30))
        window.blit(raceTimer, text_rect)
        winner = display_font_2.render('Player ' + str(playerNum + 1) + ' wins!', True, YELLOW)
        text_rect = winner.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
        window.blit(winner, text_rect)

    if phase == 2:
        # Update all projectile sprites
        allVehicleSprites.update()

    if phase >= 2:
        # Update all vehicle sprites
        allProjectileSprites.update()

        # Update score of all players
        for player in players:
            player.updateScore()

        # Display progress bar for each player
        progress_bar1.blit(progress_bar_im1, progress_bar_pos1)
        window.blit(progress_bar1, (5, 5))
        progress_bar_pos1.x = players[0].score / track1.maxRaceLength * PROGRESS_BAR_SIZE[0]
        lap = ' lap' if players[0].score <= 1.0 else ' laps'
        player1Progress = 'Player ' + str(1) + ': ' + str("{:.2f}".format(players[0].score)) + lap
        window.blit(display_font_4.render(player1Progress, True, PLAYER1_COL), (5, 15))

        progress_bar2.blit(progress_bar_im2, progress_bar_pos2)
        window.blit(progress_bar2, (WINDOW_WIDTH - PROGRESS_BAR_SIZE[0] - 5, 5))
        progress_bar_pos2.x = players[1].score / track1.maxRaceLength * PROGRESS_BAR_SIZE[0]
        lap = ' lap' if players[1].score <= 1.0 else ' laps'
        player2Progress = 'Player ' + str(2) + ': ' + str("{:.2f}".format(players[1].score)) + lap
        window.blit(display_font_4.render(player2Progress, True, PLAYER2_COL), (WINDOW_WIDTH - PROGRESS_BAR_SIZE[0] - 5, 15))

        # Display information about position of vehicles from each player
        if DISPLAY_DEBUG == 1:
            y_displ = 2
            for player in players:
                vehicleGroup = player.vehicleGroup
                for vehicle in vehicleGroup:
                    vehicleInfo = 'Player ' + str(player.playerNum + 1) + ', Lap: ' + str(vehicle.lap) + ', Speed: ' + str(round(vehicle.speed, 2)) + 'px/frame, Segment: ' + str(vehicle.seg) + ', ksi: ' + str(round(vehicle.ksi, 2)) + ', lat: ' + str(round(vehicle.lat, 2)) + ', angle: ' + str(round(-vehicle.dir * 180 / math.pi, 1)) + 'deg, Distance: ' + str(round(vehicle.distance, 2)) + ', Score: ' + str(round(player.score, 2))
                    window.blit(display_font_1.render(vehicleInfo, True, YELLOW), (2, y_displ))
                    y_displ += 14

    # Draw sprites and update display
    allProjectileSprites.draw(window)
    allVehicleSprites.draw(window)
    pygame.display.update()
    clock.tick(FPS)
    pygame.display.flip()

    # Update current time
    currentTime = time.time()

    # Update phase
    if phase == 1 and COUNTDOWN + startTime - currentTime <= 0.0:
        phase = 2
        startTime = time.time() - EPSILON
    elif phase == 2 and RACE_DURATION + startTime - currentTime <= 1.0:  # Exit loop when countdown is over
        phase = 3
        for player in players:  # Force all vehicles to slow down and stop
            for vehicle in player.vehicleGroup:
                vehicle.speedUpdate = [0, vehicle.speed, 0.0, VEHICLE_SPEED_PARAMS[5], 1]
        playerNum = 0 if players[0].score > players[1].score else 1  # Determine the winning player

pygame.quit()
