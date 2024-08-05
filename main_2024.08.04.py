import pygame
import sys
import random
import math
import time
from PIL import Image  # Used to get width and height of the window

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
YELLOW2 = (127, 127, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 153, 255)  # Used as color for the stars
PLAYER1_COL = (255, 87, 12)  # Used for player 1 progress bar
PLAYER2_COL = (0, 169, 252)  # Used for player 2 progress bar

# Constants
FPS = 30  # Frame rate of the game (frames per second)
N_STARS = 1000
N_ROCKETS = 5  # Number of rockets per player
COUNTDOWN = 3  # Used for 3... 2... 1... counter
RACE_DURATION = 60  # Race duration (s)
PROGRESS_BAR_SIZE = [300, 10]  # Width x height (px) of progress bars
TOP_BANNER_HEIGHT = 55  # Height of the top banner
EPSILON = 1e-5  # Used to clean up the race countdowns
ROCKET_WIDTH = 80  # Width of each rocket (px)
ROCKET_COUNTDOWN_OFFSET = 25  # Vertical offset used for the display of the penalty countdown (px)
VESSEL_WIDTH = 100  # Width of each vessel (px)
FLAME_MAX_WIDTH = 100  # Maximum width of the flame (px)
FRUIT_WIDTH = 50  # Width of each fruit when in the game (px)
FRUIT_ICON_WIDTH = 30  # Width of each fruit when used as upcoming fruit indicator (px)
FRUIT_ICON_SPACING = 35  # Spacing between each upcoming fruit indicator
FRUIT_ICON_SCALE = 1.2  # Used to define rectangle showing upcoming fruit
N_FRUIT_INDICATOR = 5  # Number of upcoming fruits to show
Y_ICONS = 14  # Vertical position of upcoming fruits indicators
STAR_BASE_COLOR = pygame.color.Color(PINK)  # Used to define stars
STAR_BASE_COLOR_H, STAR_BASE_COLOR_S, STAR_BASE_COLOR_V, STAR_BASE_COLOR_A = STAR_BASE_COLOR.hsva  # Used to define stars
WORLD_SIZE = 1000  # Used to define stars
DISTANCE_TO_VIEWING_PLANE = 200  # Used to define stars
STAR_SIZE = 2  # Used to define stars
STAR_SPEED = 1  # Used to define stars
STAR_ANGLE = -0.0016  # Used to define stars
DISPLAY_DEBUG = 0  # Used to determine if debug data shall be displayed on the window
ROCKET_SPEED = 4  # Used in menus (px/frame)
FRUIT_SPEED = 4  # Used in menus (px/frame)
SPAWN_INTERVAL = 1000  # Used in menus
SPAWN_CHANCE_FRUIT = 0.50  # Used in menus
RULES_MENU_FRUIT_SPEED = 0.05  # Used in "rules" menu (rad/frame)
VESSEL_WIGGLE_PARAM = [100, 25, 6.0]  # Used in "name" screen (px, px, s)

# Rocket definition
ROCKET_FILENAMES = ['Rocket01.png', 'Rocket02.png']

# 0: Average rocket speed (px/frame)
# 1: Probability that a rocket will change its speed on the track
# 2: Minimum value of speed ratio
# 3: Maximum value of speed ratio
# 4: Minimum absolute value of the acceleration ratio
# 5: Maximum absolute value of the acceleration ratio
ROCKET_SPEED_PARAMS = [6, 0.02, 0.6, 1.4, 0.01, 0.03]

# 0: Maximum absolute value of rocket lateral position (lat)
# 1: Probability that a rocket will change its lateral position along the width of the track
# 2: Minimum absolute value of the lateral speed ratio
# 3: Maximum absolute value of the lateral speed ratio
ROCKET_LAT_PARAMS = [0.5, 0.08, 0.01, 0.03]

# Vessel definition
VESSEL_FILENAMES = ['Vessel01.png', 'Vessel02.png']
VESSEL_FLAME_FILENAME = 'Flame.png'

# 0: Initial position of the first vessel along x (in % of the window width)
# 1: Initial position of the first vessel along y (in % of the window height)
# 2: Vessel maximum speed (px/frame)
# 3: Acceleration ratio ()
# 4: Vessel rotation speed (rad/frame)
VESSEL_PARAMS = [0.60, 0.85, 8, 0.03, 0.15]

# Fruit definition
FRUIT_FILENAMES = ['Fruit_Blueberry.png', 'Fruit_Strawberry.png', 'Fruit_Mango.png', 'Fruit_Watermelon.png', 'Fruit_Banana.png']
FRUIT_PENALTY = [2.0, 4.0, 6.0, 8.0, 10.0]  # Time penalties (s) related to each fruit
N_FRUITS = len(FRUIT_FILENAMES)  # Number of fruit varieties

# 0: Fruit linear speed (px/frame)
# 1: Maximum fruit rotation speed (rad/frame)
# 2: Latency allowed between 2 shots (s)
# 3: Speed at which rockets move when hit by a fruit (px/frame)
# 4: Alpha value of the OFF blink (rockets) and of the fruits that are not yet ready to throw (fruits)
# 5: Blinking time - ON (s)
# 6: Blinking time - OFF (s)
FRUIT_PARAMS = [12, 0.25, 1.5, 1, 63, 0.25, 0.10]

# 0: 'Boost' key
# 1: 'Rotate CCW' key
# 2: 'Rotate CW' key
# 3: 'Shoot' key
VESSEL_KEYS = [
    [pygame.K_w, pygame.K_q, pygame.K_e, pygame.K_s],
    [pygame.K_o, pygame.K_i, pygame.K_p, pygame.K_l]
]

# Track definition
TRACK_FILENAMES = ['Track00.png', 'Track01.png', 'Track02.png', 'Track03.png', 'Track03.png']

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display_font_1 = pygame.font.SysFont('times new roman', 12)
display_font_2 = pygame.font.SysFont('times new roman', 75, bold = True)
display_font_3 = pygame.font.SysFont('times new roman', 50, bold = True)
display_font_4 = pygame.font.SysFont('times new roman', 20, bold = True)
display_font_5 = pygame.font.SysFont('times new roman', 16, bold = True)
display_font_6 = pygame.font.SysFont('times new roman', 25, bold = True)
display_font_7 = pygame.font.SysFont('Comic Sans', 100, True, True)
display_font_8 = pygame.font.SysFont('Comic Sans', 20, False, True)
display_font_9 = pygame.font.SysFont('Comic Sans', 30, True, False)
display_font_10 = pygame.font.SysFont('Comic Sans', 40, True, False)
display_font_11 = pygame.font.SysFont('arial', 40)
clock = pygame.time.Clock()

# Initialize images for menus
pygame.display.set_caption('Space Jam')
background01 = pygame.image.load('menu_spacejam.png')
background02 = pygame.image.load('menu_background.png')
spacejam_image = pygame.image.load('menu_spacejam.png').convert_alpha()
play_image = pygame.image.load('menu_play.png').convert_alpha()
exit_image = pygame.image.load('menu_exit.png').convert_alpha()
rules_image = pygame.image.load('menu_rules.png').convert_alpha()
back_image = pygame.image.load('menu_back.png').convert_alpha()
start_image = pygame.image.load('menu_start.png').convert_alpha()
play_again_image = pygame.image.load('menu_playagain.png').convert_alpha()
track00_image = pygame.image.load('Track00.png').convert_alpha()
track01_image = pygame.image.load('Track01.png').convert_alpha()
track02_image = pygame.image.load('Track02.png').convert_alpha()
blackberry_jam_image = pygame.image.load('blackberry_jam.png').convert_alpha()
strawberry_jam_image = pygame.image.load('strawberry_jam.png').convert_alpha()
mixedberry_jam_image = pygame.image.load('mixedberry_jam.png').convert_alpha()
blackberry_jam_image = pygame.transform.scale(blackberry_jam_image, (int(blackberry_jam_image.get_width()) * .5, int(blackberry_jam_image.get_height() * .5)))
strawberry_jam_image = pygame.transform.scale(strawberry_jam_image, (int(strawberry_jam_image.get_width()) * .5, int(strawberry_jam_image.get_height() * .5)))
mixedberry_jam_image = pygame.transform.scale(mixedberry_jam_image, (int(mixedberry_jam_image.get_width()) * .5, int(mixedberry_jam_image.get_height() * .5)))


def defineTrack():
    global TRACK_FILENAME, TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI, TRACK_STARTING_GRID, TRACK_IMG
    TRACK_FILENAME = TRACK_FILENAMES[TRACK_NUM]
    TRACK_IMG = Image.open(TRACK_FILENAME)

    if TRACK_NUM == 0:  # Track #0
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
        TRACK_ARC_ORIENT = [0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1]  # Orientation of arc segments: +1 if CW, -1 if CCW
        TRACK_KSI = 0.77  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
        TRACK_STARTING_GRID = [3, 0.07, 0.07]  # Number of rockets next to one another on starting grid, ksi offset behind finish line for first rocket, and ksi value between each rocket

    elif TRACK_NUM == 1:  # Track #1
        TRACK_SEG_TYPES = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]  # Segment types: 1 = straight lines, 2 = arc (1st segment shall be a straight line)
        TRACK_TRANS_POINTS = [
            [110.0, 565.0, 125.0],
            [110.0, 195.0, 125.0],
            [175.0, 130.0, 125.0],
            [285.0, 130.0, 125.0],
            [350.0, 195.0, 125.0],
            [350.0, 220.0, 125.0],
            [415.0, 285.0, 125.0],
            [595.0, 285.0, 125.0],
            [644.8, 261.8, 125.0],
            [740.1, 148.2, 125.0],
            [789.9, 125.0, 125.0],
            [1115.0, 125.0, 100.0],
            [1180.0, 190.0, 100.0],
            [1180.0, 310.0, 100.0],
            [1147.5, 366.3, 100.0],
            [1022.1, 438.7, 100.0],
            [989.6, 495.0, 100.0],
            [989.6, 555.0, 100.0],
            [924.6, 620.0, 100.0],
            [790.0, 620.0, 100.0],
            [733.7, 587.5, 100.0],
            [684.6, 502.5, 125.0],
            [628.3, 470.0, 125.0],
            [568.0, 470.0, 125.0],
            [526.2, 485.2, 125.0],
            [371.8, 614.8, 125.0],
            [330.0, 630.0, 125.0],
            [175.0, 630.0, 125.0]
        ]  # Track transition points: (x, y) coordinates, and track width
        TRACK_ARC_DATA = [
            [0.0, 0.0, 0.0],
            [175.0, 195.0, 65.0],
            [0.0, 0.0, 0.0],
            [285.0, 195.0, 65.0],
            [0.0, 0.0, 0.0],
            [415.0, 220.0, 65.0],
            [0.0, 0.0, 0.0],
            [595.0, 220.0, 65.0],
            [0.0, 0.0, 0.0],
            [789.9, 190.0, 65.0],
            [0.0, 0.0, 0.0],
            [1115.0, 190.0, 65.0],
            [0.0, 0.0, 0.0],
            [1115.0, 310.0, 65.0],
            [0.0, 0.0, 0.0],
            [1054.6, 495.0, 65.0],
            [0.0, 0.0, 0.0],
            [924.6, 555.0, 65.0],
            [0.0, 0.0, 0.0],
            [790.0, 555.0, 65.0],
            [0.0, 0.0, 0.0],
            [628.3, 535.0, 65.0],
            [0.0, 0.0, 0.0],
            [568.0, 535.0, 65.0],
            [0.0, 0.0, 0.0],
            [330.0, 565.0, 65.0],
            [0.0, 0.0, 0.0],
            [175.0, 565.0, 65.0]
        ]  # Center points and radius of curvature for arc segments: (x, y, R)
        TRACK_ANGLES = [-1.571, -1.571, 0.000, 0.000, 1.571, 1.571, 0.000, 0.000, -0.873, -0.873, 0.000, 0.000, 1.571, 1.571, 2.618, 2.618, 1.571, 1.571, -3.142, -3.142, -2.094, -2.094, -3.142, -3.142, 2.443, 2.443, -3.142, -3.142]  # Start angles for each segment (rad)
        TRACK_ARC_ORIENT = [0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 0, 1]  # Orientation of arc segments: +1 if CW, -1 if CCW
        TRACK_KSI = 0.95  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
        TRACK_STARTING_GRID = [3, 0.10, 0.10]  # Number of rockets next to one another on starting grid, ksi offset behind finish line for first rocket, and ksi value between each rocket

    elif TRACK_NUM == 2:  # Track #2
        TRACK_SEG_TYPES = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]  # Segment types: 1 = straight lines, 2 = arc (1st segment shall be a straight line)
        TRACK_TRANS_POINTS = [
            [302.0, 174.6, 160.0],
            [968.0, 580.4, 160.0],
            [1020.0, 595.0, 160.0],
            [1060.0, 595.0, 160.0],
            [1160.0, 495.0, 160.0],
            [1160.0, 240.0, 120.0],
            [1060.0, 140.0, 120.0],
            [1020.0, 140.0, 120.0],
            [964.4, 156.9, 120.0],
            [305.6, 598.1, 120.0],
            [250.0, 615.0, 120.0],
            [210.0, 615.0, 120.0],
            [110.0, 515.0, 120.0],
            [110.0, 260.0, 160.0],
            [210.0, 160.0, 160.0],
            [250.0, 160.0, 160.0]
        ]  # Track transition points: (x, y) coordinates, and track width
        TRACK_ARC_DATA = [
            [0.0, 0.0, 0.0],
            [1020.0, 495.0, 100.0],
            [0.0, 0.0, 0.0],
            [1060.0, 495.0, 100.0],
            [0.0, 0.0, 0.0],
            [1060.0, 240.0, 100.0],
            [0.0, 0.0, 0.0],
            [1020.0, 240.0, 100.0],
            [0.0, 0.0, 0.0],
            [250.0, 515.0, 100.0],
            [0.0, 0.0, 0.0],
            [210.0, 515.0, 100.0],
            [0.0, 0.0, 0.0],
            [210.0, 260.0, 100.0],
            [0.0, 0.0, 0.0],
            [250.0, 260.0, 100.0]
        ]  # Center points and radius of curvature for arc segments: (x, y, R)
        TRACK_ANGLES = [0.548, 0.548, 0.000, 0.000, -1.571, -1.571, -3.142, -3.142, 2.552, 2.552, -3.142, -3.142, -1.571, -1.571, 0.000, 0.000]  # Start angles for each segment (rad)
        TRACK_ARC_ORIENT = [0, -1, 0, -1, 0, -1, 0, -1, 0, 1, 0, 1, 0, 1, 0, 1]  # Orientation of arc segments: +1 if CW, -1 if CCW
        TRACK_KSI = 0.90  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
        TRACK_STARTING_GRID = [3, 0.07, 0.07]  # Number of rockets next to one another on starting grid, ksi offset behind finish line for first rocket, and ksi value between each rocket

    elif TRACK_NUM == 3:  # Track #3 (slanted oval)
        TRACK_SEG_TYPES = [1, 2, 1, 2]  # Segment types: 1 = straight lines, 2 = arc (1st segment shall be a straight line)
        TRACK_TRANS_POINTS = [
            [350.0, 200.0, 75.0],
            [830.0, 200.0, 125.0],
            [776.6, 541.7, 125.0],
            [319.5, 395.2, 75.0]
        ]  # Track transition points: (x, y) coordinates, and track width
        TRACK_ARC_DATA = [
            [0.0, 0.0, 0.0],
            [830.0, 375.0, 175.0],
            [0.0, 0.0, 0.0],
            [350.0, 300.0, 100.0]
        ]  # Center points and radius of curvature for arc segments: (x, y, R)
        TRACK_ANGLES = [0.000, 0.000, -2.831, -2.831]  # Start angles for each segment (rad)
        TRACK_ARC_ORIENT = [0, 1, 0, 1]  # Orientation of arc segments: +1 if CW, -1 if CCW
        TRACK_KSI = 0.5  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
        TRACK_STARTING_GRID = [3, 0.10, 0.10]  # Number of rockets next to one another on starting grid, ksi offset behind finish line for first rocket, and ksi value between each rocket

    elif TRACK_NUM == 4:  # Track #4 (used for main menu)
        TRACK_SEG_TYPES = [1, 2, 1, 2]  # Segment types: 1 = straight lines, 2 = arc (1st segment shall be a straight line)
        TRACK_TRANS_POINTS = [
            [350.0, 50.0, 100.0],
            [930.0, 50.0, 100.0],
            [930.0, 600.0, 100.0],
            [350.0, 600.0, 100.0]
        ]  # Track transition points: (x, y) coordinates, and track width
        TRACK_ARC_DATA = [
            [0.0, 0.0, 0.0],
            [930.0, 325.0, 275.0],
            [0.0, 0.0, 0.0],
            [350.0, 325.0, 275.0]
        ]  # Center points and radius of curvature for arc segments: (x, y, R)
        TRACK_ANGLES = [0.000, 0.000, -3.142, -3.142]  # Start angles for each segment (rad)
        TRACK_ARC_ORIENT = [0, 1, 0, 1]  # Orientation of arc segments: +1 if CW, -1 if CCW
        TRACK_KSI = 0.5  # ksi at start/finish line (on first segment, assumed straight, and not near the very end of the straight to help with the lap counter)
        TRACK_STARTING_GRID = [3, 0.10, 0.10]  # Number of rockets next to one another on starting grid, ksi offset behind finish line for first rocket, and ksi value between each rocket


class Track():
    def __init__(self):
        self.segTypes = []
        self.transPoints = [[]]  # Track transition points: (x, y) coordinates, and track width
        self.nSeg = 0  # Number of segments
        self.arcData = [[]]  # Center points and radius of curvature for arc segments: (x, y, R)
        self.angles = []  # Start angles for each segment (rad)
        self.arcOrient = []  # Orientation of arc segments: +1 if CW, -1 if CCW
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
        self.arcOrient = arcOrient  # Orientation of arc segments: +1 if CW, -1 if CCW
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
                if (self.arcOrient[seg] == 1 and dTheta < 0):  # If the segment is CW and the end angle is smaller than the start angle
                    dTheta += 2 * math.pi
                if (self.arcOrient[seg] == -1 and dTheta > 0):  # If the segment is CCW and the end angle is larger than the start angle
                    dTheta -= 2 * math.pi
                segLen = self.arcData[seg][2] * abs(dTheta)  # Length of current segment: L = R * theta
                self.segLen.append(segLen)
            self.trackLen += segLen  # Update track total length
        self.maxRaceLength = RACE_DURATION * FPS * ROCKET_SPEED_PARAMS[0] * ROCKET_SPEED_PARAMS[3] / self.trackLen  # Maximum race length (number of laps)


class Rocket(pygame.sprite.Sprite):
    def __init__(self, rocketFilename, playerNum, ksi, lat, speedUpdate):
        super().__init__()
        self.playerNum = playerNum
        self.imageInit = []
        self.imageInit.append(pygame.image.load(rocketFilename).convert_alpha())
        self.imageInit.append(pygame.image.load(rocketFilename).convert_alpha())
        imgSize = self.imageInit[0].get_size()
        self.imageInit[0] = pygame.transform.scale(self.imageInit[0], (int(ROCKET_WIDTH), int(ROCKET_WIDTH * imgSize[1] / imgSize[0])))
        self.imageInit[1] = pygame.transform.scale(self.imageInit[0], (int(ROCKET_WIDTH), int(ROCKET_WIDTH * imgSize[1] / imgSize[0])))
        self.imageInit[1].set_alpha(FRUIT_PARAMS[4])
        self.image = pygame.transform.rotate(self.imageInit[0], -track1.angles[0]*180/math.pi)
        self.rect = self.image.get_rect()
        self.seg = 0  # Starts at segment 0
        self.ksi = ksi  # Rocket position at the start/finish line
        self.lat = lat  # Rocket lateral position at the start/finish line
        self.latUpdate = [0, 0, 0, 0]  # Is the lateral position currently being updated? If yes: start position, end position, acceleration ratio
        self.speed = 0  # Rocket speed (starts at rest on the starting grid)
        self.speedUpdate = speedUpdate # [x, x, x, x, x] - 0. Is the speed currently being updated? If yes: 1. start speed, 2. end speed, 3. acceleration ratio. 4. Is the rocket being forced to stop (=1) or slow down due to being hit (=2)?
        self.lastHitTime = 0  # Last time the rocket has been hit
        rocketCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
        self.rect.center = (rocketCoords[0], rocketCoords[1])  # Initial position of the rocket
        self.dir = rocketCoords[2]  # Initial direction of the rocket (rad)
        self.lap = 0  # Lap number
        self.distance = 0  # Distance covered by the rocket
        self.lastBlinkTime = 0  # Last time the rocket changed its blinking state
        self.blinkState = 0  # Blinking state (0. Fully opaque, 1. Translucent)
        self.timePenalty = 0  # Used to determine the time penalty when it is hit by a fruit; depends on the type of fruit hitting the rocket
        self.timePenaltyCountdown = 0  # Used as a time penatly countdown for a rocket that has been hit

    def update(self):
        # Update speed
        if self.speedUpdate[4] != 1:  # If the rocket is not being forced to stop
            if self.speedUpdate[4] == 2:  # If the rocket has been hit
                self.timePenaltyCountdown = self.timePenalty - currentTime + self.lastHitTime + 1.0
                if currentTime - self.lastBlinkTime > FRUIT_PARAMS[5 + self.blinkState]:  # Update blinking state
                    self.blinkState = 1 - self.blinkState
                    self.lastBlinkTime = currentTime
                if self.timePenaltyCountdown < 1.0:  # If it has been long enough since the rocket has been hit
                    self.speedUpdate[4] = 0  # Release the rocket and set new speed
                    startSpeed = self.speed  # Start speed
                    endSpeed = random.uniform(ROCKET_SPEED_PARAMS[2], ROCKET_SPEED_PARAMS[3]) * ROCKET_SPEED_PARAMS[0]  # Pick end speed
                    accelRatio = random.uniform(ROCKET_SPEED_PARAMS[4], ROCKET_SPEED_PARAMS[5])  # Acceleration (or deceleration)
                    self.speedUpdate = [1, startSpeed, endSpeed, accelRatio, 0]
                    self.blinkState = 0
            if self.speedUpdate[0] == 0 and self.speedUpdate[4] != 2:  # If the speed is currently not being updated and if the rocket has not been hit lately
                if random.random() < ROCKET_SPEED_PARAMS[1]:
                    startSpeed = self.speed  # Start speed
                    endSpeed = random.uniform(ROCKET_SPEED_PARAMS[2], ROCKET_SPEED_PARAMS[3]) * ROCKET_SPEED_PARAMS[0]  # Pick end speed
                    accelRatio = random.uniform(ROCKET_SPEED_PARAMS[4], ROCKET_SPEED_PARAMS[5])  # Acceleration (or deceleration)
                    self.speedUpdate = [1, startSpeed, endSpeed, accelRatio, 0]
            if self.speedUpdate[0] == 1:  # If the speed is currently being updated
                self.speed += self.speedUpdate[3]*(self.speedUpdate[2] - self.speedUpdate[1])
                if ((self.speedUpdate[2] - self.speedUpdate[1] >= 0) and (self.speed >= self.speedUpdate[2])) or ((self.speedUpdate[2] - self.speedUpdate[1] < 0) and (self.speed <= self.speedUpdate[2])):  # If the speed has reached its to-be-updated-to value
                    self.speed = self.speedUpdate[2]
                    for i_par in range(4):
                        self.speedUpdate[i_par] = 0
        else:  # If the rocket is being forced to stop
            self.speed += self.speedUpdate[3] * (self.speedUpdate[2] - self.speedUpdate[1])
            if self.speed <= self.speedUpdate[2]:  # If the speed has reached 0
                self.speed = 0.0

        # Update lateral position
        if self.speedUpdate[4] == 0:  # If the rocket is not being forced to stop or to slow down because it has been hit
            if self.latUpdate[0] == 0:  # If the lateral position is currently not being updated
                if random.random() < ROCKET_LAT_PARAMS[1]:
                    startLat = self.lat  # Start lateral position
                    endLat = random.uniform(-ROCKET_LAT_PARAMS[0], ROCKET_LAT_PARAMS[0])  # Pick end lateral position
                    accelRatio = random.uniform(ROCKET_LAT_PARAMS[2], ROCKET_LAT_PARAMS[3])  # Acceleration (or deceleration)
                    self.latUpdate = [1, startLat, endLat, accelRatio]
            if self.latUpdate[0] == 1:  # If the lateral position is currently being updated
                self.lat += self.latUpdate[3]*(self.latUpdate[2] - self.latUpdate[1])
                if ((self.latUpdate[2] - self.latUpdate[1] >= 0) and (self.lat >= self.latUpdate[2]) or (self.latUpdate[2] - self.latUpdate[1] < 0) and (self.lat <= self.latUpdate[2])):
                    self.lat = self.latUpdate[2]
                    self.latUpdate = [0, 0, 0, 0]

        # Update position on the track
        distanceToCover = self.speed  # Distance by which the rocket needs to move in the time increment
        if track1.segTypes[self.seg] == 2:  # Adjust distanceToCover to take rocket's lateral position into account, if the segment is an arc:
            segPlusOne = (self.seg + 1) % track1.nSeg  # Index of next segment
            trackWidth = track1.transPoints[self.seg][2] + self.ksi * (track1.transPoints[segPlusOne][2] - track1.transPoints[self.seg][2])  # Track width
            distanceToCover = distanceToCover * track1.arcData[self.seg][2] / (track1.arcData[self.seg][2] - track1.arcOrient[self.seg] * self.lat * trackWidth / 2)
        while distanceToCover > 0:
            newKsi = self.ksi + distanceToCover / track1.segLen[self.seg]
            if newKsi < 1:  # If the rocket is still in the same segment
                if (self.seg == 0 and self.ksi < track1.startKsi and newKsi >= track1.startKsi):  # Update lap number
                    self.lap += 1
                self.ksi = newKsi
                newCoords = natToGlobal(track1, self.seg, self.ksi, self.lat)
                self.dir = newCoords[2]
                self.image = pygame.transform.rotate(self.imageInit[self.blinkState], -self.dir * 180 / math.pi) # Orient the rocket according to the local orientation of the track
                self.rect = self.image.get_rect()
                self.rect.center = (newCoords[0], newCoords[1])
                distanceToCover = 0
            else:  # If the rocket is now in the next segment
                distanceToCover -= track1.segLen[self.seg] * (1 - self.ksi)
                self.seg = (self.seg + 1) % track1.nSeg  # Move to the next segment
                self.ksi = 0.0

        # Calculate distance covered by rocket (updated only once the rocket has crossed the start line for the first time, and only if the rocket is not being forced to stop once the race timer has timed out)
        if self.lap >= 1 and self.speedUpdate[4] != 1:
            self.distance = (self.lap - 1) * track1.trackLen - TRACK_KSI * track1.segLen[0] + self.ksi * track1.segLen[self.seg]
            for iSeg in range(self.seg):
                self.distance += track1.segLen[iSeg]
            if self.seg == 0 and self.ksi < TRACK_KSI:
                self.distance += track1.trackLen



class Vessel(pygame.sprite.Sprite):
    def __init__(self, vesselFilename, playerNum, initPosition):
        super().__init__()
        self.playerNum = playerNum
        self.speed = 0  # Speed of the vessel
        self.dir = -math.pi/2  # Direction w.r.t. horizontal (rad)
        self.imageInit = pygame.image.load(vesselFilename).convert_alpha()
        imgSize = self.imageInit.get_size()
        self.imageInit = pygame.transform.scale(self.imageInit, (int(VESSEL_WIDTH), int(VESSEL_WIDTH * imgSize[1] / imgSize[0])))
        self.image = pygame.transform.rotate(self.imageInit, -self.dir * 180 / math.pi - 90)
        self.rect = self.image.get_rect()
        self.height = self.rect.height  # Height of the vessel before rotation (used to position the flame behind it)
        self.initPosition = initPosition  # Initial position of the rocket
        self.rect.center = self.initPosition
        self.lastShotTime = 0  # Time of the last projectile shot
        self.phase = 0  # Phase of the vessel: 0 when in play, 1 if game has ended, 2 when used in "name" screen
        self.t_wiggle = 0  # Time used for vessel wiggling in "name" screen
        self.delta_t = random.uniform(0, VESSEL_WIGGLE_PARAM[2])  # Time desynchronizing for vessel wiggling in "name" screen (s)

    def update(self, keys):
        if self.phase <= 1:  # If the vessel is in play or if the game has ended
            # Update vessel speed
            if keys[VESSEL_KEYS[self.playerNum][0]]:  # If boosters are on, accelerate but limit the speed to its maximum value
                self.speed += VESSEL_PARAMS[2] * VESSEL_PARAMS[3]
                if self.speed > VESSEL_PARAMS[2]:
                    self.speed = VESSEL_PARAMS[2]
            else:  # Boosters are off
                self.speed -= VESSEL_PARAMS[2] * VESSEL_PARAMS[3]
                if self.speed < 0:
                    self.speed = 0

            # Update vessel orientation
            if keys[VESSEL_KEYS[self.playerNum][1]]:  # Rotating vessel CCW
                self.dir -= VESSEL_PARAMS[4]
            if keys[VESSEL_KEYS[self.playerNum][2]]:  # Rotating vessel CW
                self.dir += VESSEL_PARAMS[4]

            # Calculate new coordinates
            newCoords = [self.rect.centerx + self.speed * math.cos(self.dir), self.rect.centery + self.speed * math.sin(self.dir)]
            if newCoords[0] < self.rect.width / 2:
                newCoords[0] = self.rect.width / 2
            if newCoords[0] > WINDOW_WIDTH - self.rect.width / 2:
                newCoords[0] = WINDOW_WIDTH - self.rect.width / 2
            if newCoords[1] < TOP_BANNER_HEIGHT + self.rect.height / 2:
                newCoords[1] = TOP_BANNER_HEIGHT + self.rect.height / 2
            if newCoords[1] > WINDOW_HEIGHT - self.rect.height/2:
                newCoords[1] = WINDOW_HEIGHT - self.rect.height/2
            self.image = pygame.transform.rotate(self.imageInit, -self.dir * 180 / math.pi - 90)
            self.rect = self.image.get_rect()
            self.rect.center = (newCoords[0], newCoords[1])

            # Shoot fruit
            if keys[VESSEL_KEYS[self.playerNum][3]] and time.time() - self.lastShotTime > FRUIT_PARAMS[2] and self.phase == 0:
                self.lastShotTime = time.time()
                fruit = Fruit(self.rect.center, self.dir, players[self.playerNum].upcomingFruits[0], 1, 0, self.playerNum)  # Throw next fruit
                players[self.playerNum].upcomingFruits.pop(0)  # Remove fruit that was thrown and from list of upcoming fruits
                players[self.playerNum].upcomingFruits.append(random.randint(0, N_FRUITS - 1))  # Randomly picks upcoming fruit to list of upcoming fruits
                allProjectileSprites.add(fruit)  # Add fruit that was thrown to group of fruits

                # Updates indicators for upcoming fruits
                allUpcomingFruitSprites[self.playerNum] = pygame.sprite.Group()
                for fruitNum in range(N_FRUIT_INDICATOR):
                    if self.playerNum == 0:
                        coords = (PROGRESS_BAR_SIZE[0] + (N_FRUIT_INDICATOR - fruitNum) * FRUIT_ICON_SPACING, Y_ICONS)
                    else:
                        coords = (WINDOW_WIDTH - PROGRESS_BAR_SIZE[0] + (fruitNum - N_FRUIT_INDICATOR) * FRUIT_ICON_SPACING, Y_ICONS)
                    fruitIcon = Fruit(coords, math.pi / 2, players[self.playerNum].upcomingFruits[fruitNum], 2, 1, self.playerNum)
                    allUpcomingFruitSprites[self.playerNum].add(fruitIcon)
        else:  # If the vessel is used in the "name" screen
            self.t_wiggle += 1 / FPS
            self.rect.center = self.initPosition
            self.rect.centerx += VESSEL_WIGGLE_PARAM[0] * (1 + math.cos((self.t_wiggle - self.delta_t) * 2 * math.pi / VESSEL_WIGGLE_PARAM[2]))
            self.rect.centery += VESSEL_WIGGLE_PARAM[1] * math.sin(2 * (self.t_wiggle - self.delta_t) * 2 * math.pi / VESSEL_WIGGLE_PARAM[2])

class Flame(pygame.sprite.Sprite):
    def __init__(self, playerNum):
        super().__init__()
        self.playerNum = playerNum
        self.speed = players[self.playerNum].vessel.speed
        self.dir = players[self.playerNum].vessel.dir  # Direction w.r.t. horizontal (rad)
        self.imageInit = pygame.image.load(VESSEL_FLAME_FILENAME).convert_alpha()
        self.imgSize = self.imageInit.get_size()
        self.image = pygame.transform.scale(self.imageInit, (int(FLAME_MAX_WIDTH * self.speed / VESSEL_PARAMS[2]), int(FLAME_MAX_WIDTH * self.imgSize[1] / self.imgSize[0] * self.speed / VESSEL_PARAMS[2])))
        self.image = pygame.transform.rotate(self.image, -self.dir * 180 / math.pi - 90)
        self.rect = self.image.get_rect()
        self.rect.center = players[self.playerNum].vessel.rect.center  # Initial position of the flame
        flameHeight = int(FLAME_MAX_WIDTH * self.imgSize[1] / self.imgSize[0] * self.speed / VESSEL_PARAMS[2])
        offset = (players[self.playerNum].vessel.height + flameHeight) / 2
        self.rect.centerx -= offset * math.cos(self.dir)
        self.rect.centery -= offset * math.sin(self.dir)

    def update(self):
        # Update flame position, orientation and size
        self.speed = players[self.playerNum].vessel.speed
        self.dir = players[self.playerNum].vessel.dir  # Direction w.r.t. horizontal (rad)
        flameHeight = int(FLAME_MAX_WIDTH * self.imgSize[1] / self.imgSize[0] * self.speed / VESSEL_PARAMS[2])
        self.image = pygame.transform.scale(self.imageInit, (int(FLAME_MAX_WIDTH * self.speed / VESSEL_PARAMS[2]), flameHeight))
        self.image = pygame.transform.rotate(self.image, -self.dir * 180 / math.pi - 90)
        self.rect = self.image.get_rect()
        self.rect.center = players[self.playerNum].vessel.rect.center  # Initial position of the flame
        offset = (players[self.playerNum].vessel.height + flameHeight) / 2
        self.rect.centerx -= offset * math.cos(self.dir)
        self.rect.centery -= offset * math.sin(self.dir)


class Fruit(pygame.sprite.Sprite):
    def __init__(self, initPosition, initDir, type, inGame, waitBeforeThrow, playerNum):
        super().__init__()
        self.type = type  # Type of fruit
        self.inGame = inGame  # Determines if the fruit is 1. in the game, 2. used as an upcoming fruit indicator, 3. in the goodbye menu or 4. in the rules menu
        self.playerNum = playerNum  # Records the number of the player that threw the fruit
        self.dir = initDir  # Direction in which the fruit is moving
        self.angle = 0  # Orientation of the fruit (rad)
        self.rotSpeed = random.uniform(-FRUIT_PARAMS[1], FRUIT_PARAMS[1])  # Pick random rotation speed (rad/frame)
        self.imageInit = []
        self.imageInit.append(pygame.image.load(FRUIT_FILENAMES[self.type]).convert_alpha())
        self.imageInit.append(pygame.image.load(FRUIT_FILENAMES[self.type]).convert_alpha())
        imgSize = self.imageInit[0].get_size()
        if inGame == 1 or inGame == 3  or inGame == 4:
            widthHeight = (int(FRUIT_WIDTH), int(FRUIT_WIDTH * imgSize[1] / imgSize[0]))
        else:
            widthHeight = (int(FRUIT_ICON_WIDTH), int(FRUIT_ICON_WIDTH * imgSize[1] / imgSize[0]))
        self.imageInit[0] = pygame.transform.scale(self.imageInit[0], widthHeight)
        self.imageInit[1] = pygame.transform.scale(self.imageInit[1], widthHeight)
        self.imageInit[1].set_alpha(FRUIT_PARAMS[4])
        self.image = pygame.transform.rotate(self.imageInit[0], self.angle * 180 / math.pi)
        self.rect = self.image.get_rect()
        self.rect.center = initPosition  # Initial position of the fruit
        self.waitBeforeThrow = waitBeforeThrow  # =0 if the fruit is in the game or used to indicate upcoming fruits ready to throw; =1 if the fruit is used to indicate upcoming fruits that are not yet ready to throw

    def update(self):
        if self.inGame == 1:  # Fruit is in the game
            # Update fruit position and orientation
            if -self.rect.width < self.rect.x < WINDOW_WIDTH and TOP_BANNER_HEIGHT < self.rect.y < WINDOW_HEIGHT:
                self.angle += self.rotSpeed
                newCoords = [self.rect.centerx + FRUIT_PARAMS[0] * math.cos(self.dir), self.rect.centery + FRUIT_PARAMS[0] * math.sin(self.dir)]
                self.image = pygame.transform.rotate(self.imageInit[0], -self.angle * 180 / math.pi)
                self.rect = self.image.get_rect()
                self.rect.center = (newCoords[0], newCoords[1])
            else:  # Destroy the fruit if it reaches the edges of the window
                self.kill()
        elif self.inGame == 2:  # Fruit is used as an indicator
            # Update fruit transparency depending on whether it is ready to throw
            if time.time() - players[self.playerNum].vessel.lastShotTime > FRUIT_PARAMS[2]:
                self.waitBeforeThrow = 0
            self.image = pygame.transform.rotate(self.imageInit[self.waitBeforeThrow], -self.angle * 180 / math.pi)
        elif self.inGame == 3:  # Fruit is used as rain in menu
            if -self.rect.width < self.rect.x < WINDOW_WIDTH and self.rect.y < WINDOW_HEIGHT:
                self.angle += self.rotSpeed
                newCoords = [self.rect.centerx + FRUIT_PARAMS[0] * math.cos(self.dir), self.rect.centery + FRUIT_PARAMS[0] * math.sin(self.dir)]
                self.image = pygame.transform.rotate(self.imageInit[0], -self.angle * 180 / math.pi)
                self.rect = self.image.get_rect()
                self.rect.center = (newCoords[0], newCoords[1])
            else:  # Destroy the fruit if it reaches the edges of the window
                self.kill()
        elif self.inGame == 4:  # Fruit is used in "rules" page
            self.angle += self.rotSpeed
            newCoords = [self.rect.centerx, self.rect.centery]
            self.image = pygame.transform.rotate(self.imageInit[0], -self.angle * 180 / math.pi)
            self.rect = self.image.get_rect()
            self.rect.center = (newCoords[0], newCoords[1])


class Player():
    def __init__(self, playerNum, rocketGroup, vessel):
        self.playerNum = playerNum
        self.name = 'Player ' + str(int(self.playerNum))
        self.rocketGroup = rocketGroup
        self.score = 0.00  # Score (out of 100)
        self.vessel = vessel
        self.upcomingFruits = []
        for fruitNum in range(N_FRUIT_INDICATOR):
            self.upcomingFruits.append(random.randint(0, N_FRUITS - 1))  # Randomly picks upcoming fruits

    # Update the score of a player
    def updateScore(self):
        self.score = 0.00
        for rocket in self.rocketGroup:
            self.score += rocket.distance / track1.trackLen
        self.score = self.score / N_ROCKETS


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
        star_window_x, star_window_y = self.perspectiveTransform()
        pygame.draw.circle(window, color, (int(star_window_x), int(star_window_y)), STAR_SIZE)


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False


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
            if endAngle < startAngle:  # If the segment is CW and the end angle is smaller than the start angle
                endAngle += 2 * math.pi
            theta = startAngle + ksi * (endAngle - startAngle)
            x = track.arcData[seg][0] + track.arcData[seg][2] * math.cos(theta - math.pi / 2) - lat * trackWidth/2 * math.sin(theta)
            y = track.arcData[seg][1] + track.arcData[seg][2] * math.sin(theta - math.pi / 2) + lat * trackWidth/2 * math.cos(theta)
        if track.arcOrient[seg] == -1:
            if endAngle > startAngle:  # If the segment is CCW and the end angle is larger than the start angle
                endAngle -= 2 * math.pi
            theta = startAngle + ksi * (endAngle - startAngle)
            x = track.arcData[seg][0] + track.arcData[seg][2] * math.cos(theta + math.pi / 2) - lat * trackWidth/2 * math.sin(theta)
            y = track.arcData[seg][1] + track.arcData[seg][2] * math.sin(theta + math.pi / 2) + lat * trackWidth/2 * math.cos(theta)
    return [x, y, theta]

def detectCollisions():
    collidedRockets = pygame.sprite.groupcollide(allProjectileSprites, allRocketSprites, False, False, pygame.sprite.collide_mask)
    if collidedRockets:  # If fruits hit some Rockets
        for fruit_i, rocket_i in collidedRockets.items():
            if rocket_i[0].speedUpdate[4] != 2:  # If the rocket has not yet been hit in the past few seconds
                rocket_i[0].speedUpdate = [1, rocket_i[0].speed, FRUIT_PARAMS[3], ROCKET_SPEED_PARAMS[5], 2]
                rocket_i[0].lastHitTime = time.time()  # Update last time the rocket has been hit
                rocket_i[0].lastBlinkTime = rocket_i[0].lastHitTime
                rocket_i[0].blinkState = 0  # Starts to make the rocket blink
                rocket_i[0].timePenalty = FRUIT_PENALTY[fruit_i.type]  # Define the time penalty
                fruit_i.kill()  # Kill the fruit


def drawPenaltyCountdowns():
    for playerNum in range(2):
        for rocket in players[playerNum].rocketGroup:  # For all rockets belonging to player self.playerNum
            if rocket.speedUpdate[4] == 2:  # If the rocket has been hit
                penaltyCountdown = display_font_6.render(str(int(rocket.timePenaltyCountdown)), True, YELLOW, BLACK)
                countdownPos = [rocket.rect.centerx, rocket.rect.centery - (rocket.rect.height / 2 + ROCKET_COUNTDOWN_OFFSET)]
                text_rect = penaltyCountdown.get_rect(center=countdownPos)
                window.blit(penaltyCountdown, text_rect)


def spawn_fruit():
    if random.random() < SPAWN_CHANCE_FRUIT:
        current_spawn_time = pygame.time.get_ticks()
        if current_spawn_time - last_spawn_time > SPAWN_INTERVAL:
            fruit = Fruit((random.randint(0, WINDOW_WIDTH), 0), math.pi/2, random.randint(0, N_FRUITS - 1),  3, 0, 0)
            allProjectileSprites.add(fruit)


# Main menu page (starting window)
def main_page():
    # Global variables
    global allRocketSprites, allVesselSprites, allFlameSprites, allProjectileSprites, allUpcomingFruitSprites, coordsUpcomingFruits, players, winningPlayerNum, track1, playerNum, currentTime, last_spawn_time, TRACK_NUM, playerName

    currentTime = time.time()

    # Create the track
    TRACK_NUM = 4
    defineTrack()
    track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)

    # Initialize players
    players = []  # List of all players
    playerName = ['', '']

    # Create groups of sprites
    allRocketSprites = pygame.sprite.Group()  # All rocket sprites
    allVesselSprites = pygame.sprite.Group()  # All vessel sprites
    allFlameSprites = pygame.sprite.Group()  # All flame sprites
    allProjectileSprites = pygame.sprite.Group()  # All projectile sprites in the window
    allUpcomingFruitSprites = []  # All fruit sprites used to indicate upcoming projectiles
    coordsUpcomingFruits = []  # List of coordinates for time penalty indicators below upcoming fruit indicators

    # Create Buttons
    play_button = Button(WINDOW_WIDTH // 2, (WINDOW_HEIGHT // 2) + 50, play_image, 0.5)
    exit_button = Button(WINDOW_WIDTH // 2, (WINDOW_HEIGHT // 2) + 150, exit_image, 0.25)
    rules_button = Button(WINDOW_WIDTH - 50, (WINDOW_HEIGHT - 50), rules_image, .2)

    # Create vessel sprites for main menu
    playerNum = 0
    ksi = track1.startKsi - TRACK_STARTING_GRID[1]
    if TRACK_STARTING_GRID[0] == 1:  # If only one row of rockets
        lat = 0
    else:
        lat = -ROCKET_LAT_PARAMS[0]
    i_lat = 1  # Index for lateral position
    speedUpdate = [1, 0.00, ROCKET_SPEED_PARAMS[0], ROCKET_SPEED_PARAMS[5], 0]  # Makes the rocket accelerate to target speed from 0 speed
    for i in range(2 * N_ROCKETS):
        rocket = Rocket(ROCKET_FILENAMES[playerNum], playerNum, ksi, lat, speedUpdate)
        allRocketSprites.add(rocket)  # Add rocket to group of all rocket sprites
        ksi -= TRACK_STARTING_GRID[2]
        if TRACK_STARTING_GRID[0] == 1:  # If only one row of rockets
            lat = 0
        else:
            i_lat = i_lat % TRACK_STARTING_GRID[0] + 1
            lat = -ROCKET_LAT_PARAMS[0] + 2 * (i_lat - 1) / (TRACK_STARTING_GRID[0] - 1) * ROCKET_LAT_PARAMS[0]
        playerNum = 1 - playerNum  # Switch player

    last_spawn_time = pygame.time.get_ticks()
    while True:
        window.blit(background01, background01.get_rect())
        play_button.draw(window)
        exit_button.draw(window)
        rules_button.draw(window)

        allRocketSprites.update()
        allRocketSprites.draw(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif play_button.is_clicked(event):
                name_page()

            elif exit_button.is_clicked(event):
                goodbye_page()

            elif rules_button.is_clicked(event):
                rules_page()

        pygame.display.update()
        clock.tick(FPS)


# Exit page
def goodbye_page():
    global allRocketSprites, allVesselSprites, allFlameSprites, allProjectileSprites, allUpcomingFruitSprites, coordsUpcomingFruits, players, winningPlayerNum, track1, playerNum, currentTime, last_spawn_time, TRACK_NUM, playerName

    timer = 0

    # Empty groups of sprites
    allRocketSprites.empty()
    allVesselSprites.empty()
    allFlameSprites.empty()
    allProjectileSprites.empty()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        window.blit(background02, background02.get_rect())

        clock.tick(FPS)
        timer += 1/FPS

        allProjectileSprites.update()
        allProjectileSprites.draw(window)

        if timer < 5.0:
            spawn_fruit()

        elif 5.0 <= timer <= 8.0:
            text_surface = display_font_7.render("GOODBYE!", True, WHITE)
            window.blit(text_surface, (150, 200))

        else:
            pygame.quit()
            sys.exit()

        pygame.display.update()


# Function used to wrap text in rectangle of specified dimensions
def drawText(surface, text, color, rect, font, aa=True, bkg=None):
    y = rect.top
    lineSpacing = -2

    # Get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # Determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # Determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # If we have wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # Render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # Remove the text we just blitted
        text = text[i:]

    return text


# Game rules page
def rules_page():
    global allRocketSprites, allVesselSprites, allFlameSprites, allProjectileSprites, allUpcomingFruitSprites, coordsUpcomingFruits, players, winningPlayerNum, track1, playerNum, currentTime, last_spawn_time, TRACK_NUM, playerName

    back_button = Button(50, WINDOW_HEIGHT - 50, back_image, 0.2)

    # Empty groups of sprites
    allRocketSprites.empty()
    allVesselSprites.empty()
    allFlameSprites.empty()
    allProjectileSprites.empty()

    for fruitNum in range(N_FRUITS):
        fruit = Fruit((300, 250 + 75 * fruitNum), math.pi / 2, fruitNum, 4, 0, 0)
        fruit.rotSpeed = RULES_MENU_FRUIT_SPEED
        allProjectileSprites.add(fruit)

    text_surface01 = display_font_9.render('GAMEPLAY', True, WHITE)
    game_objective_text = "Objective: Race your opponent with your fleet of rockets before time runs out. The fleet that completes the most laps wins. Sabotage your opponent by moving your vessel and throwing fruits at their rockets. Be careful not to hit your own rockets!"
    game_objective_text_rect = pygame.rect.Rect(50, 100, WINDOW_WIDTH - 100, 130)
    while True:
        window.blit(background02, background02.get_rect())
        back_button.draw(window)

        # Game Objective
        pygame.draw.rect(window, GRAY, pygame.rect.Rect(30, 30, WINDOW_WIDTH - 60, 150), 75, 10)

        window.blit(text_surface01, ((WINDOW_WIDTH / 2) - (text_surface01.get_width() / 2), 50))
        drawText(window, game_objective_text, WHITE, game_objective_text_rect, display_font_8)

        # Fruits
        allProjectileSprites.update()
        allProjectileSprites.draw(window)

        for fruitNum in range(N_FRUITS):
            text_surface = display_font_9.render('Slows opponent for ' + str(int(FRUIT_PENALTY[fruitNum])) + ' seconds', True, YELLOW)
            window.blit(text_surface, (375, 232 + 75 * fruitNum))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif back_button.is_clicked(event):
                return

        pygame.display.update()


# Enter player name page
def name_page():
    global allRocketSprites, allVesselSprites, allFlameSprites, allProjectileSprites, allUpcomingFruitSprites, coordsUpcomingFruits, players, winningPlayerNum, track1, playerNum, currentTime, last_spawn_time, TRACK_NUM, playerName

    # Empty groups of sprites
    allRocketSprites.empty()
    allVesselSprites.empty()
    allFlameSprites.empty()
    allProjectileSprites.empty()

    # User input box
    player1_text = playerName[0]
    player2_text = playerName[1]
    player1_input_rect = pygame.Rect(460, 198, 250, 50)
    player2_input_rect = pygame.Rect(460, 348, 250, 50)
    player1_color_active = pygame.Color(PLAYER1_COL)
    player2_color_active = pygame.Color(PLAYER2_COL)
    color_passive = pygame.Color(WHITE)
    active_player1 = False
    active_player2 = False

    # Background images
    player1_image = pygame.image.load('player1_image.png').convert_alpha()
    player1_image = pygame.transform.scale(player1_image, (int(player1_image.get_width() * .30), int(player1_image.get_height() * .30)))

    player2_image = pygame.image.load('player2_image.png').convert_alpha()
    player2_image = pygame.transform.scale(player2_image, (int(player2_image.get_width() * .30), int(player2_image.get_height() * .30)))

    start_button = Button(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150, start_image, .5)
    back_button = Button(50, WINDOW_HEIGHT - 50, back_image, .2)

    for playerNum in range(2):
        vessel = Vessel(VESSEL_FILENAMES[playerNum], playerNum, [750, 220 + playerNum * 150])
        vessel.phase = 2  # The vessel is used in the "name" screen
        allVesselSprites.add(vessel)  # Add vessel to group of all vessel sprites

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if player1_input_rect.collidepoint(event.pos):
                    active_player1 = True
                    active_player2 = False
                elif player2_input_rect.collidepoint(event.pos):
                    active_player1 = False
                    active_player2 = True
                else:
                    active_player1 = False
                    active_player2 = False

            if event.type == pygame.KEYDOWN:
                if active_player1:
                    if event.key == pygame.K_BACKSPACE:
                        player1_text = player1_text[:-1]
                    else:
                        player1_text += event.unicode
                elif active_player2:
                    if event.key == pygame.K_BACKSPACE:
                        player2_text = player2_text[:-1]
                    else:
                        player2_text += event.unicode

            if start_button.is_clicked(event):
                playerName[0] = player1_text
                playerName[1] = player2_text
                choose_track_page()

            if back_button.is_clicked(event):
                main_page()

        window.blit(background02, background02.get_rect())

        pygame.draw.rect(window, player1_color_active if active_player1 else color_passive, player1_input_rect)
        pygame.draw.rect(window, player2_color_active if active_player2 else color_passive, player2_input_rect)
        text_surface1 = display_font_11.render(player1_text, True, BLACK)
        text_surface2 = display_font_11.render(player2_text, True, BLACK)
        window.blit(text_surface1, (player1_input_rect.x + 10, player1_input_rect.y + 5))
        window.blit(text_surface2, (player2_input_rect.x + 10, player2_input_rect.y + 5))
        player1_input_rect.w = max(200, text_surface1.get_width() + 10)
        player2_input_rect.w = max(200, text_surface2.get_width() + 10)

        window.blit(player1_image, (200, 200))
        window.blit(player2_image, (205, 350))

        start_button.draw(window)
        back_button.draw(window)

        # Vessels
        keys = pygame.key.get_pressed()
        allVesselSprites.update(keys)
        allVesselSprites.draw(window)

        pygame.display.update()


# Track page
def choose_track_page():
    global allRocketSprites, allVesselSprites, allFlameSprites, allProjectileSprites, allUpcomingFruitSprites, coordsUpcomingFruits, players, winningPlayerNum, track1, playerNum, currentTime, last_spawn_time, TRACK_NUM, playerName

    # Create buttons
    track00_button = Button(300, 175, track00_image, 0.2)
    track01_button = Button(300, 350, track01_image, 0.2)
    track02_button = Button(300, 525, track02_image, 0.2)
    back_button = Button(50, WINDOW_HEIGHT - 50, back_image, .2)

    # Background settings
    text_surface = display_font_10.render("CHOOSE YOUR TRACK:", True, WHITE)

    while True:
        window.blit(background02, background02.get_rect())
        window.blit(text_surface, (200, 20))

        track00_button.draw(window)
        window.blit(blackberry_jam_image, (440, 150))

        track01_button.draw(window)
        window.blit(strawberry_jam_image, (450, 325))

        track02_button.draw(window)
        window.blit(mixedberry_jam_image, (450, 500))

        back_button.draw(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif track00_button.is_clicked(event):
                TRACK_NUM = 0
                defineTrack()
                track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)
                start_race()
            elif track01_button.is_clicked(event):
                TRACK_NUM = 1
                defineTrack()
                track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)
                start_race()
            elif track02_button.is_clicked(event):
                TRACK_NUM = 2
                defineTrack()
                track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)
                start_race()
            elif back_button.is_clicked(event):
                return
        pygame.display.update()


def start_race():
    global allRocketSprites, allVesselSprites, allFlameSprites, allProjectileSprites, allUpcomingFruitSprites, coordsUpcomingFruits, players, winningPlayerNum, track1, playerNum, currentTime, last_spawn_time, TRACK_NUM, playerName

    background = pygame.image.load(TRACK_FILENAME)

    # Empty groups of sprites
    allRocketSprites.empty()
    allVesselSprites.empty()
    allFlameSprites.empty()
    allProjectileSprites.empty()

    players = []  # List of all players

    for playerNum in range(2):
        allUpcomingFruitSprites.append(pygame.sprite.Group())
        coordsUpcomingFruits.append([])

    # Create vessels and players
    winningPlayerNum = 0  # Used to record the winning player
    for playerNum in range(2):
        vessel = Vessel(VESSEL_FILENAMES[playerNum], playerNum, [WINDOW_WIDTH * (playerNum * VESSEL_PARAMS[0] + (1 - playerNum) * (1 - VESSEL_PARAMS[0])), WINDOW_HEIGHT * VESSEL_PARAMS[1]])
        allVesselSprites.add(vessel)  # Add vessel to group of all vessel sprites
        player = Player(playerNum, pygame.sprite.Group(), vessel)
        player.name = playerName[playerNum]
        players.append(player)
        flame = Flame(playerNum)
        allFlameSprites.add(flame)  # Add vessel to group of all flame sprites
        for fruitNum in range(N_FRUIT_INDICATOR):  # Defines indicators for upcoming fruits
            if playerNum == 0:
                coords = (PROGRESS_BAR_SIZE[0] + (N_FRUIT_INDICATOR - fruitNum) * FRUIT_ICON_SPACING, Y_ICONS)
            else:
                coords = (WINDOW_WIDTH - PROGRESS_BAR_SIZE[0] + (fruitNum - N_FRUIT_INDICATOR) * FRUIT_ICON_SPACING, Y_ICONS)
            fruitIcon = Fruit(coords, math.pi/2, players[playerNum].upcomingFruits[fruitNum], 2, 0, playerNum)
            allUpcomingFruitSprites[playerNum].add(fruitIcon)
            coordsUpcomingFruits[playerNum].append([coords[0], coords[1] + FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH / 2 + 7])

    # Create rockets for each player and add to groups
    playerNum = random.randint(0, 1)  # Randomly picks player in first place on starting grid
    ksi = track1.startKsi - TRACK_STARTING_GRID[1]
    if TRACK_STARTING_GRID[0] == 1:  # If only one row of rockets
        lat = 0
    else:
        lat = -ROCKET_LAT_PARAMS[0]
    i_lat = 1  # Index for lateral position
    speedUpdate = [1, 0.00, ROCKET_SPEED_PARAMS[0], ROCKET_SPEED_PARAMS[5], 0]  # Makes the rocket accelerate to target speed from 0 speed
    for i in range(2 * N_ROCKETS):
        rocket = Rocket(ROCKET_FILENAMES[playerNum], playerNum, ksi, lat, speedUpdate)
        players[playerNum].rocketGroup.add(rocket)  # Add rocket to rocket group of appropriate player
        allRocketSprites.add(rocket)  # Add rocket to group of all rocket sprites
        ksi -= TRACK_STARTING_GRID[2]
        if TRACK_STARTING_GRID[0] == 1:  # If only one row of rockets
            lat = 0
        else:
            i_lat = i_lat % TRACK_STARTING_GRID[0] + 1
            lat = -ROCKET_LAT_PARAMS[0] + 2 * (i_lat - 1)/(TRACK_STARTING_GRID[0] - 1) * ROCKET_LAT_PARAMS[0]
        playerNum = 1 - playerNum  # Switch player

    # Define stars
    stars = []
    for i in range(N_STARS):
        stars.append(Star())

    # Define progress bars
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

    # Main loop
    phase = 1  # 1:  3... 2... 1... countdown phase; 2: game phase; 3: post-game phase
    startTime = time.time()
    currentTime = time.time()
    play_again_button = Button(WINDOW_WIDTH // 2, 400, play_again_image, 0.5)
    exit_button = Button(WINDOW_WIDTH // 2, 525, exit_image, 0.35)
    while True:
        pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        # Update current time
        currentTime = time.time()

        # Update phase
        if phase == 1 and COUNTDOWN + startTime - currentTime <= 0.0:
            phase = 2
            startTime = time.time() - EPSILON
        elif phase == 2 and RACE_DURATION + startTime - currentTime <= 1.0:  # Exit loop when countdown is over
            phase = 3
            for player in players:  # Force all rockets to slow down and stop, and force all vessels to enter their phase 1 (game has ended)
                for rocket in player.rocketGroup:
                    rocket.speedUpdate = [0, rocket.speed, 0.0, ROCKET_SPEED_PARAMS[5], 1]
                player.vessel.phase = 1  # Game has ended
            winningPlayerNum = 0 if players[0].score > players[1].score else 1  # Determine the winning player

        # Update and draw stars
        for star in stars:
            star.update()
            star.draw(window)

        window.blit(background, background.get_rect())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif play_again_button.is_clicked(event):
                name_page()
            elif exit_button.is_clicked(event):
                goodbye_page()

        if phase == 1:  # 3... 2... 1... countdown phase
            # Display 3... 2... 1... countdown
            countdown = display_font_2.render(" " + str(int(COUNTDOWN + startTime - currentTime + 1)) + '... ', True, WHITE, BLACK)
            text_rect = countdown.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
            window.blit(countdown, text_rect)
        else:  # Race phase or post-game phase (phase 2 or 3)
            pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BANNER_HEIGHT))
            pygame.draw.rect(window, YELLOW2, pygame.Rect(PROGRESS_BAR_SIZE[0] + N_FRUIT_INDICATOR * FRUIT_ICON_SPACING - FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH / 2, Y_ICONS - FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH / 2, FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH, FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH))
            pygame.draw.rect(window, YELLOW2, pygame.Rect(WINDOW_WIDTH - PROGRESS_BAR_SIZE[0] - N_FRUIT_INDICATOR * FRUIT_ICON_SPACING - FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH / 2, Y_ICONS - FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH / 2, FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH, FRUIT_ICON_SCALE * FRUIT_ICON_WIDTH))

            # Display race timer
            if phase == 2:
                raceTimerTxt = str(int(RACE_DURATION + startTime - currentTime))
            else:
                raceTimerTxt = "0"
            raceTimer = display_font_3.render(raceTimerTxt, True, YELLOW)
            text_rect = raceTimer.get_rect(center=(WINDOW_WIDTH / 2, 30))
            window.blit(raceTimer, text_rect)

            # Handle pressed keys and update all sprites
            keys = pygame.key.get_pressed()
            allRocketSprites.update()  # Update all rocket sprites
            allVesselSprites.update(keys)  # Update all vessel sprites
            allFlameSprites.update()  # Update all flame sprites
            allProjectileSprites.update()  # Update all projectile sprites

            # Detect collisions between fruits and rockets
            if phase == 2:
                detectCollisions()

            # Update score of all players
            for player in players:
                player.updateScore()

            # Display progress bar for each player
            progress_bar1.blit(progress_bar_im1, progress_bar_pos1)
            window.blit(progress_bar1, (5, 5))
            progress_bar_pos1.x = players[0].score / track1.maxRaceLength * PROGRESS_BAR_SIZE[0]
            lap = ' lap' if players[0].score <= 1.0 else ' laps'
            player1Progress = players[0].name + ': ' + str("{:.2f}".format(players[0].score)) + lap
            window.blit(display_font_4.render(player1Progress, True, PLAYER1_COL), (5, 15))

            progress_bar2.blit(progress_bar_im2, progress_bar_pos2)
            window.blit(progress_bar2, (WINDOW_WIDTH - PROGRESS_BAR_SIZE[0] - 5, 5))
            progress_bar_pos2.x = players[1].score / track1.maxRaceLength * PROGRESS_BAR_SIZE[0]
            lap = ' lap' if players[1].score <= 1.0 else ' laps'
            player2Progress = players[1].name + ': ' + str("{:.2f}".format(players[1].score)) + lap
            window.blit(display_font_4.render(player2Progress, True, PLAYER2_COL), (WINDOW_WIDTH - PROGRESS_BAR_SIZE[0] - 5, 15))

            # Display upcoming fruits in top banner
            allUpcomingFruitSprites[0].update()
            allUpcomingFruitSprites[1].update()
            allUpcomingFruitSprites[0].draw(window)
            allUpcomingFruitSprites[1].draw(window)
            for playerNum in range(2):
                for fruitNum in range(N_FRUIT_INDICATOR):
                    penalty = display_font_5.render(str(int(FRUIT_PENALTY[players[playerNum].upcomingFruits[fruitNum]])), True, WHITE)
                    text_rect = penalty.get_rect(center=coordsUpcomingFruits[playerNum][fruitNum])
                    window.blit(penalty, text_rect)

        # Draw sprites and update display
        allProjectileSprites.draw(window)
        allRocketSprites.draw(window)
        allFlameSprites.draw(window)
        allVesselSprites.draw(window)
        drawPenaltyCountdowns()  # Draws countdown of all rocket sprites that have been hit
        if phase == 3:  # Post-race phase
            COL = PLAYER1_COL if winningPlayerNum == 0 else PLAYER2_COL  # Determine color of the winning player
            winner = display_font_2.render(players[winningPlayerNum].name + ' wins!', True, COL, BLACK)
            text_rect = winner.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
            window.blit(winner, text_rect)

            play_again_button.draw(window)
            exit_button.draw(window)

        pygame.display.update()
        clock.tick(FPS)
        pygame.display.flip()

################################# MAIN PROGRAM #######################################
# Start with main page
main_page()
