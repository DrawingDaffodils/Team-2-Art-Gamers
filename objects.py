import pygame
import random
import math
import time
from constants import * #asterisk allows your to import global variable, classes, and functions forma file.



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
    def __init__(self, vehicleFilename, playerId, ksi, lat, speedUpdate):
        super().__init__()
        self.playerId = playerId
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
    def __init__(self, vesselFilename, playerId, initPosition):
        super().__init__()
        self.playerId = playerId
        self.dir = math.pi/2  # Direction w.r.t. horizontal (rad)
        self.imageInit = pygame.image.load(vesselFilename).convert_alpha()
        imgSize = self.imageInit.get_size()
        self.image = pygame.transform.scale(self.imageInit, (int(VESSEL_WIDTH), int(VESSEL_WIDTH * imgSize[1] / imgSize[0])))
        self.rect = self.image.get_rect()
        self.rect.center = initPosition  # Initial position of the vehicle
        self.lastShotTime = 0  # Time of the last projectile shot

    def update(self):
        # Listen for movement and send it to websocket server
        movement = {"y": self.rect.y, "x": self.rect.x, "dir": self.dir }
        keys = pygame.key.get_pressed()
        if keys[VESSEL_KEYS[0]] and self.rect.y > TOP_BANNER_HEIGHT:
            movement['y'] -= VESSEL_PARAMS[2]  # move up
            movement['dir'] = math.pi/2
        if keys[VESSEL_KEYS[1]] and self.rect.y < WINDOW_HEIGHT - self.rect.height:
            movement['y'] += VESSEL_PARAMS[2]  # move down
            movement['dir'] = -math.pi / 2
        if keys[VESSEL_KEYS[2]] and self.rect.x > 0:
            movement['x'] -= VESSEL_PARAMS[2]  # move left
            movement['dir'] = math.pi
        if keys[VESSEL_KEYS[3]] and self.rect.x < WINDOW_WIDTH - self.rect.width:
            movement['x'] += VESSEL_PARAMS[2]  # move right
            movement['dir'] = 0

        # Shoot fruit
        if keys[VESSEL_KEYS[4]] and time.time() - self.lastShotTime > FRUIT_PARAMS[2]:
            self.lastShotTime = time.time()
            fruit = Fruit(self.rect.center, self.dir, 0)
            allProjectileSprites.add(fruit)

        # Sends data to server.py
        sio.emit('update', movement)


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
    def __init__(self, playerId, vehicleGroup, vessel):
        self.playerId = playerId
        self.vehicleGroup = vehicleGroup
        self.score = 0.00  # Score (out of 100)
        self.vessel = vessel

    # Update the score of a player
    def updateScore(self):
        self.score = 0.00
        for vehicle in self.vehicleGroup:
            self.score += vehicle.distance / track1.trackLen
        self.score = self.score / N_VEHICLES
        sio.emit('update', {"score": self.score})

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

#Are lines 244 to 271 for vehiclae mathematics for the vehicles?
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

track1 = Track(TRACK_SEG_TYPES, TRACK_TRANS_POINTS, TRACK_ARC_DATA, TRACK_ANGLES, TRACK_ARC_ORIENT, TRACK_KSI)
allVehicleSprites = pygame.sprite.Group()  # All vehicle and vessel sprites
allProjectileSprites = pygame.sprite.Group()  # All projectile sprites
ksi = track1.startKsi - TRACK_STARTING_GRID[1]