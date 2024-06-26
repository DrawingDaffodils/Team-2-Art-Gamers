import pygame
import random
import math
from PIL import Image  # Used to get width and height of the window

# Constants
FPS = 30  # Frame rate of the game (frames per second)
AVE_CAR_SPEED = 6  # Average car speed (px/frame)
YELLOW = (255, 255, 0)

# Car definition
CAR_FILENAME = 'Circle_red.png'

# Track definition
TRACK_FILENAME = 'Track01.png'
TRACK_IMG = Image.open(TRACK_FILENAME)
WINDOW_WIDTH = TRACK_IMG.width  # 1280
WINDOW_HEIGHT = TRACK_IMG.height  # 720
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

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display_font = pygame.font.SysFont('times new roman', 20)
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


class Car(pygame.sprite.Sprite):
    def __init__(self, carFilename):
        super().__init__()
        self.imageInit = pygame.image.load(carFilename)
        self.image = pygame.transform.rotate(self.imageInit, track1.angles[0]*180/math.pi)
        self.rect = self.image.get_rect()

        self.seg = 0  # Starts at segment 0
        self.ksi = track1.startKsi  # Car positioned at the start/finish line
        self.lat = 0  # Car lateral position is initially 0.0 along the track width
        carCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
        self.rect.center = (carCoords[0], carCoords[1])  # Initial position of the car
        self.dir = carCoords[2]  # Initial direction of the car (rad)
        self.lap = 1  # Lap number
        self.speed = AVE_CAR_SPEED  # Car speed

    def update(self):
        distance = self.speed  # Distance by which the car needs to move
        while distance > 0:
            newKsi = self.ksi + distance / track1.segLen[self.seg]
            if newKsi < 1:  # If the car is still in the same segment
                if (self.seg == 0 and self.ksi < track1.startKsi and newKsi >= track1.startKsi):  # Update lap number
                    self.lap += 1
                self.ksi = newKsi
                newCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
                self.image = pygame.transform.rotate(self.imageInit, -newCoords[2] * 180 / math.pi) # Orient the car according to the local orientation of the track
                # self.rect = self.image.get_rect()
                self.rect.x = newCoords[0]
                self.rect.y = newCoords[1]
                distance = 0
            else:  # If the car is now in the next segment
                distance -= track1.segLen[self.seg] * (1 - self.ksi)
                self.seg = (self.seg + 1) % track1.nSeg
                self.ksi = 0.0


def natToGlobal(track, seg, ksi, lat):  # Calculates global coords (x, y, theta) from natural coords (seg, ksi, lat)
    segPlusOne = (seg + 1) % track.nSeg
    if track.segTypes[seg] == 1:  # If the segment is a straight line
        x = track.transPoints[seg][0] + ksi * (track.transPoints[segPlusOne][0] - track.transPoints[seg][0])
        y = track.transPoints[seg][1] + ksi * (track.transPoints[segPlusOne][1] - track.transPoints[seg][1])
        theta = track.angles[seg]
    else:  # If the segment is an arc
        startAngle = track.angles[seg]
        endAngle = track.angles[segPlusOne]
        if (track.arcOrient[seg] == 1 and endAngle < startAngle):  # If the segment is CCW and the end angle is smaller than the start angle
            endAngle += 2 * math.pi
        if (track.arcOrient[seg] == -1 and endAngle > startAngle):  # If the segment is CW and the end angle is larger than the start angle
            endAngle -= 2 * math.pi

        theta = startAngle + ksi * (endAngle - startAngle)
        x = track.arcData[seg][0] + track.arcData[seg][2] * math.cos(theta - math.pi/2)
        y = track.arcData[seg][1] + track.arcData[seg][2] * math.sin(theta - math.pi/2)
    return [x, y, theta]

# Create groups
car_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Create the track
track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)

# Create cars for each player and add to groups
car1 = Car(CAR_FILENAME)
car_group.add(car1)
all_sprites.add(car1)

# Main game loop
running = True
while running:
    window.blit(background, background.get_rect())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Display information about car position
    car_info = display_font.render('Lap: ' + str(car1.lap) + ', Speed: ' + str(car1.speed) + 'px/frame, Segment: ' + str(car1.seg) + ', ksi: ' + str(round(car1.ksi,2)), True, YELLOW)
    window.blit(car_info, (2, 2))

    # Update all sprites
    all_sprites.update()

    # Draw sprites and update display
    all_sprites.draw(window)
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
