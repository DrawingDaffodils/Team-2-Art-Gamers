import pygame
import random
import math
import time
from PIL import Image  # Used to get width and height of the window

# Constants
TRACK_NUM = 2  # 1 or 2
FPS = 30  # Frame rate of the game (frames per second)
N_STARS = 100
N_VEHICLES = 3  # Number of vehicles per player
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
COUNTDOWN = 3  # Used for 3... 2... 1... counter

# Vehicle definition
VEHICLE_FILENAMES = ['Rocket01.png', 'Rocket02.png']  # 'Circle_red.png'

# 0: Average vehicle speed (px/frame)
# 1: Probability that a vehicle will change its speed on the track
# 2: Minimum value of speed ratio
# 3: Maximum value of speed ratio
# 4: Minimum absolute value of the acceleration ratio
# 5: Maximum absolute value of the acceleration ratio
VEHICLE_SPEED_PARAMS = [6, 0.02, 0.6, 1.4, 0.01, 0.03]

# 0: Maximum absolute value of vehicle lateral position (lat)
# 1: Probability that a vehicle will change its lateral position along the width of the track
# 2: Minimum absolute value of the lateral speed ratio
# 3: Maximum absolute value of the lateral speed ratio
VEHICLE_LAT_PARAMS = [0.5, 0.08, 0.01, 0.03]

# Track definition
if (TRACK_NUM == 1):  # Track #1
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

elif (TRACK_NUM == 2):  # Track #2
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
    TRACK_ARC_ORIENT = [0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1]  # Orientation of arc segments: +1 if CCW, -1 if CW
    TRACK_KSI = 0.5  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
    TRACK_STARTING_GRID = [3, 1.00, 0.07, 0.07]  # Number of vehicles next to one another on starting grid, lateral spacing between all vehicles, ksi offset behind finish line for first vehicle, and ksi value between each vehicle

TRACK_IMG = Image.open(TRACK_FILENAME)
WINDOW_WIDTH = TRACK_IMG.width  # 1280
WINDOW_HEIGHT = TRACK_IMG.height  # 720

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display_font_1 = pygame.font.SysFont('times new roman', 12)
display_font_2 = pygame.font.SysFont('times new roman', 100)
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

    def __init__(self, segTypes, transPoints, arcData, angles, arcOrient, startKsi):
        self.segTypes = segTypes  # Segment types: 1 = straight lines, 2 = arc
        self.transPoints = transPoints  # Track transition points: (x, y) coordinates, and track width
        self.nSeg = len(transPoints)  # Number of segments
        self.arcData = arcData  # Center points and radius of curvature for arc segments: (x, y, R)
        self.angles = angles  # Start angles for each segment (rad)
        self.arcOrient = arcOrient  # Orientation of arc segments: +1 if CCW, -1 if CW
        self.startKsi = startKsi  # ksi at start/finish line (on first segment, assumed straight)
        self.segLen = []  # Length of each segment
        for seg in range(self.nSeg):
            segPlusOne = (seg + 1) % self.nSeg
            if self.segTypes[seg] == 1:  # If the segment is a straight line
                self.segLen.append(math.sqrt((self.transPoints[segPlusOne][0] - self.transPoints[seg][0]) ** 2 + (self.transPoints[segPlusOne][1] - self.transPoints[seg][1]) ** 2))
            else:  # If the segment is an arc
                dTheta = self.angles[segPlusOne] - self.angles[seg]
                if (self.arcOrient[seg] == 1 and dTheta < 0):  # If the segment is CCW and the end angle is smaller than the start angle
                    dTheta += 2 * math.pi
                if (self.arcOrient[seg] == -1 and dTheta > 0):  # If the segment is CW and the end angle is larger than the start angle
                    dTheta -= 2 * math.pi
                self.segLen.append(self.arcData[seg][2] * abs(dTheta))


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, vehicleFilename, player, ksi, lat):
        super().__init__()
        self.player = player
        self.imageInit = pygame.image.load(vehicleFilename)
        self.image = pygame.transform.rotate(self.imageInit, track1.angles[0]*180/math.pi)
        self.rect = self.image.get_rect()
        self.seg = 0  # Starts at segment 0
        self.ksi = ksi  # Vehicle position at the start/finish line
        self.lat = lat  # Vehicle lateral position at the start/finish line
        self.latUpdate = [0, 0, 0, 0]  # Is the lateral position currently being updated? If yes: start position, end position, acceleration ratio
        self.speed = VEHICLE_SPEED_PARAMS[0]  # Vehicle speed
        self.speedUpdate = [0, 0, 0, 0]  # Is the speed currently being updated? If yes: start speed, end speed, acceleration ratio
        vehicleCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
        self.rect.center = (vehicleCoords[0], vehicleCoords[1])  # Initial position of the vehicle
        self.dir = vehicleCoords[2]  # Initial direction of the vehicle (rad)
        self.lap = 1  # Lap number

    def update(self):
        # Update speed
        if self.speedUpdate[0] == 0:  # If the speed is currently not being updated
            if random.random() < VEHICLE_SPEED_PARAMS[1]:
                startSpeed = self.speed  # Start speed
                endSpeed = random.uniform(VEHICLE_SPEED_PARAMS[2], VEHICLE_SPEED_PARAMS[3]) * VEHICLE_SPEED_PARAMS[0]  # Pick end speed
                accelRatio = random.uniform(VEHICLE_SPEED_PARAMS[4], VEHICLE_SPEED_PARAMS[5])  # Acceleration (or deceleration)
                self.speedUpdate = [1, startSpeed, endSpeed, accelRatio]
        if self.speedUpdate[0] == 1:  # If the speed is currently being updated
            self.speed += self.speedUpdate[3]*(self.speedUpdate[2] - self.speedUpdate[1])
            if ((self.speedUpdate[2] - self.speedUpdate[1] >= 0) and (self.speed >= self.speedUpdate[2]) or (self.speedUpdate[2] - self.speedUpdate[1] < 0) and (self.speed <= self.speedUpdate[2])):
                self.speed = self.speedUpdate[2]
                self.speedUpdate = [0, 0, 0, 0]

        # Update lateral position
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

        # Update position
        distance = self.speed  # Distance by which the vehicle needs to move
        while distance > 0:
            newKsi = self.ksi + distance / track1.segLen[self.seg]
            if newKsi < 1:  # If the vehicle is still in the same segment
                if (self.seg == 0 and self.ksi < track1.startKsi and newKsi >= track1.startKsi):  # Update lap number
                    self.lap += 1
                self.ksi = newKsi
                newCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
                self.dir = newCoords[2]
                self.image = pygame.transform.rotate(self.imageInit, -self.dir * 180 / math.pi) # Orient the vehicle according to the local orientation of the track
                # self.rect = self.image.get_rect()
                self.rect.center = (newCoords[0], newCoords[1])
                distance = 0
            else:  # If the vehicle is now in the next segment
                distance -= track1.segLen[self.seg] * (1 - self.ksi)
                self.seg = (self.seg + 1) % track1.nSeg
                self.ksi = 0.0


class Stars():
    def __init__(self, screenwidth, screenheight):
        self.x = random.randint(0,screenwidth)
        self.y = random.randint(0,screenheight)
        self.speed = random.uniform(1,3)

    def update(self):
        self.y += self.speed
        if self.y > WINDOW_HEIGHT:
            self.y = 0
            self.x = random.randint(0, WINDOW_WIDTH)

    def draw(self, surface):  # Add star image via pygame.draw.image
        pygame.draw.circle(surface,(255, 255, 255), (self.x, self.y), 5)


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

# Create groups
vehicle_group1 = pygame.sprite.Group()  # All vehicles from player 1
vehicle_group2 = pygame.sprite.Group()  # All vehicles from player 2
all_sprites = pygame.sprite.Group()

# Create the track
track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)

# Create vehicles for each player and add to groups
player = random.randint(1, 2)  # Randomly picks player in first place on starting grid
ksi = track1.startKsi - TRACK_STARTING_GRID[2]
lat = -TRACK_STARTING_GRID[1]/2
i_lat = 1  # Index for lateral position
for i in range(2 * N_VEHICLES):
    vehicle = Vehicle(VEHICLE_FILENAMES[player - 1], player, ksi, lat)
    if player==1:
        vehicle_group1.add(vehicle)
    else:
        vehicle_group2.add(vehicle)
    all_sprites.add(vehicle)
    ksi -= TRACK_STARTING_GRID[3]
    i_lat = i_lat % TRACK_STARTING_GRID[0] + 1
    lat = (i_lat - 2) / (TRACK_STARTING_GRID[0] - 1) * TRACK_STARTING_GRID[1]
    player = 3 - player  # Switch player

# Define stars
stars = [Stars(WINDOW_WIDTH, WINDOW_HEIGHT) for _ in range(N_STARS)]

# 3... 2... 1... countdown
running = True
start_time = time.time()
current_time = time.time()
while running:
    window.blit(background, background.get_rect())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw stars
    for star in stars:
        star.update()
        star.draw(window)

    # Display countdown
    countdown = display_font_2.render(str(int(COUNTDOWN + start_time - current_time + 1)) + '...', True, BLACK)
    text_rect = countdown.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    window.blit(countdown, text_rect)

    # Draw sprites and update display
    all_sprites.draw(window)
    pygame.display.update()
    clock.tick(FPS)

    # Exit loop when countdown is over
    current_time = time.time()
    if COUNTDOWN + start_time - current_time <= 0.0:
        running = False

# Main game loop
running = True
while running:
    window.blit(background, background.get_rect())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw stars
    for star in stars:
        star.update()
        star.draw(window)

    # Display information about position of vehicles from each player
    y_displ = 2
    for vehicle in vehicle_group1:
        vehicle_info = display_font_1.render('Player 1, Lap: ' + str(vehicle.lap) + ', Speed: ' + str(round(vehicle.speed, 2)) + 'px/frame, Segment: ' + str(vehicle.seg) + ', ksi: ' + str(round(vehicle.ksi, 2)) + ', lat: ' + str(round(vehicle.lat, 2)) + ', angle: ' + str(round(-vehicle.dir * 180 / math.pi, 1)) + 'deg', True, YELLOW)
        window.blit(vehicle_info, (2, y_displ))
        y_displ += 14
    for vehicle in vehicle_group2:
        vehicle_info = display_font_1.render('Player 2, Lap: ' + str(vehicle.lap) + ', Speed: ' + str(round(vehicle.speed, 2)) + 'px/frame, Segment: ' + str(vehicle.seg) + ', ksi: ' + str(round(vehicle.ksi, 2)) + ', lat: ' + str(round(vehicle.lat, 2)) + ', angle: ' + str(round(-vehicle.dir * 180 / math.pi, 1)) + 'deg', True, YELLOW)
        window.blit(vehicle_info, (2, y_displ))
        y_displ += 14

    # Update all sprites
    all_sprites.update()

    # Draw sprites and update display
    all_sprites.draw(window)
    pygame.display.update()
    clock.tick(FPS)


pygame.quit()
