from constants import *
from objects import *
import time
import random


sio.connect("http://localhost:8080") # Connects the websocket client to server.py

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display_font_1 = pygame.font.SysFont('times new roman', 12)
display_font_2 = pygame.font.SysFont('times new roman', 75, bold = True)
display_font_3 = pygame.font.SysFont('times new roman', 50, bold = True)
display_font_4 = pygame.font.SysFont('times new roman', 20, bold = True)
clock = pygame.time.Clock()

background = pygame.image.load(TRACK_FILENAME)

players = {}  # List of all players

playerNum = 0
playerId = ''
    

@sio.client.on('player_data')
def player_data(data):
    
    global players
    global playerId
    playerId = sio.sid
    for key, playerData in data.items():
        playerNum = playerData['playerNum']
        if key in players.keys():
            player = players[key]
            vessel = player.vessel
        else:
            vessel = Vessel(VESSEL_FILENAMES[playerNum], key, [playerData['x'], playerData['y']])
            player = Player(playerNum, pygame.sprite.Group(), vessel)
        
        player.score = playerData['score']
        vessel.rect.x = playerData['x']
        vessel.rect.y = playerData['y']
        vessel.dir = playerData['dir']
        players[key] = player
        

time.sleep(2)
print(players)




# Create vehicles for each player and add to groups
 # Randomly picks player in first place on starting grid
ksi = track1.startKsi - TRACK_STARTING_GRID[1]
if TRACK_STARTING_GRID[0] == 1:  # If only one row of vehicles
    lat = 0
else:
    lat = -VEHICLE_LAT_PARAMS[0]
i_lat = 1  # Index for lateral position
speedUpdate = [1, 0.00, VEHICLE_SPEED_PARAMS[0], VEHICLE_SPEED_PARAMS[5], 0] # Makes the vehicle accelerate to target speed from 0 speed
for i in range(2 * N_VEHICLES):
    vehicle = Vehicle(VEHICLE_FILENAMES[playerNum], playerId, ksi, lat, speedUpdate)
    players[playerId].vehicleGroup.add(vehicle)  # Add vehicle to vehicle group of appropriate player
    allVehicleSprites.add(vehicle)  # Add vehicle to group of all vehicle sprites
    ksi -= TRACK_STARTING_GRID[2]
    if TRACK_STARTING_GRID[0] == 1:  # If only one row of vehicles
        lat = 0
    else:
        i_lat = i_lat % TRACK_STARTING_GRID[0] + 1
        lat = -VEHICLE_LAT_PARAMS[0] + 2 * (i_lat - 1)/(TRACK_STARTING_GRID[0] - 1) * VEHICLE_LAT_PARAMS[0]
    # playerNum = 1 - playerNum  # Switch player


# Add vessels to allVehicleSprites after vehicles have already been added, so they appear on top
for key, player in players.items():
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
        for key, player in players.items():
            player.updateScore()

        # Display progress bar for each player
        for key, player in players.items():
            name = str(player.playerId)
            playerNum = player.playerId
            progress_bar1.blit(progress_bar_im1, progress_bar_pos1)
            window.blit(progress_bar1, (5, 5))
            progress_bar_pos1.x = player.score / track1.maxRaceLength * PROGRESS_BAR_SIZE[0]
            lap = ' lap' if players[key].score <= 1.0 else ' laps'
            playerProgress = 'Player ' + name + ': ' + str("{:.2f}".format(player.score)) + lap
            window.blit(display_font_4.render(playerProgress, True, PLAYER1_COL), (5, 15))

        
        # Display information about position of vehicles from each player
        if DISPLAY_DEBUG == 1:
            y_displ = 2
            for key, player in players.items():
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
        for key, player in players.items():  # Force all vehicles to slow down and stop
            for vehicle in player.vehicleGroup:
                vehicle.speedUpdate = [0, vehicle.speed, 0.0, VEHICLE_SPEED_PARAMS[5], 1]
        playerNum = 0 if players[0].score > players[1].score else 1  # Determine the winning player

sio.disconnect()
pygame.quit()
