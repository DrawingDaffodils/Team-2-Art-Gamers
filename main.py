from constants import *
from objects import *
import time
import random







# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
display_font_1 = pygame.font.SysFont('times new roman', 12)
display_font_2 = pygame.font.SysFont('times new roman', 75, bold = True)
display_font_3 = pygame.font.SysFont('times new roman', 50, bold = True)
display_font_4 = pygame.font.SysFont('times new roman', 20, bold = True)
clock = pygame.time.Clock()

background = pygame.image.load(TRACK_FILENAME)

players: dict[str, Player] = {}  # List of all players

playerNum = 0
playerId = None
phase = 1  # 1:  3... 2... 1... waiting for player phase; 2: game phase; 3: post-game phase



# Runs on every tick from server.py
@sio.on('player_data')
def player_data(data): 
    create_players(data)
        


def fruit_exists(id: str) -> bool:
    for fruit in allProjectileSprites:
        if fruit.id == id:
            return True
    return False

def create_players(data: dict):
    global players, playerNumm
    for key, playerData in data.items():
        num = playerData['playerNum']
        if key is playerId:
            playerNum = num
        # Check is player & vessel already exists, If they dont, create them.
        if key in players.keys(): # If player exists just use the already made one
            player = players[key]
            vessel = player.vessel
            
        else: # if it doesnt, create them.  
            vessel = Vessel(
                VESSEL_FILENAMES[num], 
                initPosition=[playerData['x'], playerData['y']], 
                id=key,
                playerId=playerId)
            player = Player(key, pygame.sprite.Group(), vessel, num)
        vessel.playerId = playerId
        player.score = playerData['score']
        vessel.rect.x = playerData['x']
        vessel.rect.y = playerData['y']
        
        vessel.dir = playerData['dir']
        
        
        
        players[key] = player
        if 'fruits' in playerData and playerData['fruits']:
            for id, fruitData in playerData['fruits'].items():
                if fruitData and not fruit_exists(id):
                    
                    initPosition = fruitData['initPosition']
                    initDir = fruitData['initDir']
                    fruitType = fruitData['type']
                    fruit = Fruit(initPosition, initDir, fruitType, id)
                    allProjectileSprites.add(fruit)

# Create vehicles for each player and add to groups
 # Randomly picks player in first place on starting grid
def create_vehicles():
    global players   
    ksi = track1.startKsi - TRACK_STARTING_GRID[1]
    if TRACK_STARTING_GRID[0] == 1:  # If only one row of vehicles
        lat = 0
    else:
        lat = -VEHICLE_LAT_PARAMS[0]
    i_lat = 1  # Index for lateral position
    speedUpdate = [1, 0.00, VEHICLE_SPEED_PARAMS[0], VEHICLE_SPEED_PARAMS[5], 0] # Makes the vehicle accelerate to target speed from 0 speed
    for id, player in players.items():
        print(player)
        player = players[id]
        # Only create vehicles if that player doesnt have any
        if len(player.vehicleGroup) != 0:
            pass

        for i in range(N_VEHICLES):
            vehicle = Vehicle(VEHICLE_FILENAMES[player.playerNum], id, ksi, lat, speedUpdate)
            player.vehicleGroup.add(vehicle)  # Add vehicle to vehicle group of appropriate player
            allVehicleSprites.add(vehicle)  # Add vehicle to group of all vehicle sprites
            ksi -= TRACK_STARTING_GRID[2]
            if TRACK_STARTING_GRID[0] == 1:  # If only one row of vehicles
                lat = 0
            else:
                i_lat = i_lat % TRACK_STARTING_GRID[0] + 1
                lat = -VEHICLE_LAT_PARAMS[0] + 2 * (i_lat - 1)/(TRACK_STARTING_GRID[0] - 1) * VEHICLE_LAT_PARAMS[0]
        allVehicleSprites.add(player.vessel)  # Add vessel to group of all vehicle sprites
        # playerNum = 1 - playerNum  # Switch player


stars = []
def create_stars():
    global stars
    for i in range(N_STARS):
        stars.append(Star())

# Main loop

running = True
winner = None

startTime = None
currentTime = time.time()


@sio.on('start')
def start(data):
    print('Recieved start')
    global startTime, phase, players, playerId
    allProjectileSprites.empty()
    allVehicleSprites.empty()
    players = {}
    playerId = data['id']
    
    create_stars()

    players_data = data['players']
    create_players(players_data)
    create_vehicles()
    startTime = data['startTime']
    
    
    phase = 2
    print('More than 2 players connected, ready to go')

@sio.on('race_over')
def race_over(data):
    global winner, phase
    winner = data['winner']
    phase = 3




sio.connect(SOCKETIO_URL) # Connects the websocket client to server.py
while running:
    pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    window.blit(background, background.get_rect())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sio.disconnect()

    # Update and draw stars
    for star in stars:
        star.update()
        star.draw(window)

    if phase == 1:  # Waiting phase
        countdown = display_font_2.render('Waiting for more players to join...', True, WHITE)
        text_rect = countdown.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
        # print('Waiting for more players...')
        window.blit(countdown, text_rect)
        
    elif phase == 2:  # Race phase
        pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BANNER_HEIGHT))
        # Display race timer
        raceTimer = display_font_3.render(str(int(RACE_DURATION + startTime - currentTime)), True, YELLOW)
        text_rect = raceTimer.get_rect(center=(WINDOW_WIDTH / 2, 30))
        window.blit(raceTimer, text_rect)
    elif phase == 3 and winner:  # Post-game phase
        winner_player = players[winner['id']]
        winner_score = winner['score']
        pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BANNER_HEIGHT))
        raceTimer = display_font_3.render('0', True, YELLOW)
        text_rect = raceTimer.get_rect(center=(WINDOW_WIDTH / 2, 30))
        window.blit(raceTimer, text_rect)
        winnerText = display_font_2.render('Player ' + str(winner_player.playerNum) + ' wins!', True, player.color)
        text_rect = winnerText.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
        window.blit(winnerText, text_rect)

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
            playerNum = player.playerNum
            name = 'Player ' + str(playerNum)
            bar, bar_im, bar_pos = player.createProgressBar()

            # Define positions for each corner
            positions = [(5, 5), (window.get_width() - bar.get_width() - 5, 5),
                        (5, window.get_height() - bar.get_height() - 5), 
                        (window.get_width() - bar.get_width() - 5, 
                        window.get_height() - bar.get_height() - 5)]

            # Set the position based on playerNum
            window.blit(bar, positions[playerNum])
            bar_pos.x = player.score / track1.maxRaceLength * PROGRESS_BAR_SIZE[0]
            lap = ' lap' if player.score <= 1.0 else ' laps'
            playerProgress = 'Player ' + name + ': ' + str("{:.2f}".format(player.score)) + lap
            window.blit(display_font_4.render(playerProgress, True, player.color), (5, 15))

        
        # Display information about position of vehicles from each player
        # if DISPLAY_DEBUG == 1:
        #     y_displ = 2
        #     for key, player in players.items():
        #         vehicleGroup = player.vehicleGroup
        #         for vehicle in vehicleGroup:
        #             vehicleInfo = 'Player ' + str(player.playerNum + 1) + ', Lap: ' + str(vehicle.lap) + ', Speed: ' + str(round(vehicle.speed, 2)) + 'px/frame, Segment: ' + str(vehicle.seg) + ', ksi: ' + str(round(vehicle.ksi, 2)) + ', lat: ' + str(round(vehicle.lat, 2)) + ', angle: ' + str(round(-vehicle.dir * 180 / math.pi, 1)) + 'deg, Distance: ' + str(round(vehicle.distance, 2)) + ', Score: ' + str(round(player.score, 2))
        #             window.blit(display_font_1.render(vehicleInfo, True, YELLOW), (2, y_displ))
        #             y_displ += 14

    # Draw sprites and update display
    allProjectileSprites.draw(window)
    allVehicleSprites.draw(window)
    pygame.display.update()
    clock.tick(FPS)
    pygame.display.flip()

    # Update current time
    currentTime = time.time()

    

    if phase == 2 and winner and RACE_DURATION + startTime - currentTime <= 1.0:  # Exit loop when countdown is over
        # phase = 3
        for key, player in players.items():  # Force all vehicles to slow down and stop
            for vehicle in player.vehicleGroup:
                vehicle.speedUpdate = [0, vehicle.speed, 0.0, VEHICLE_SPEED_PARAMS[5], 1]
        # playerNum = 0 if players[0].score > players[1].score else 1  # Determine the winning player

pygame.quit()
