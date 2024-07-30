import pygame
from PIL import Image
import socketio  # Used to get width and height of the window

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PINK = (255, 153, 255)
# PLAYER1_COL = (255, 87, 12)  # Used for player 1 progress bar
# PLAYER2_COL = (0, 169, 252)  # Used for player 2 progress bar
PLAYER_COLS = [BLUE, YELLOW, GREEN, PINK]

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
# 3: Maximum life time for fruit (s)
FRUIT_PARAMS = [10, 0.15, 0.75, 1.75]

# 0: 'Up' key
# 1: 'Down' key
# 2: 'Left' key
# 3: 'Right' key
# 4: 'Shoot' key
VESSEL_KEYS = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_x]
    # [pygame.K_o, pygame.K_l, pygame.K_k, pygame.K_SEMICOLON, pygame.K_PERIOD]


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
SOCKETIO_URL = "http://localhost:8080"

# Create Websocket client
sio = socketio.Client()