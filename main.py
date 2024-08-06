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
    for fruit in fruitGroup:
        if fruit.id == id:
            return True
    return False

def all_vehicles() -> list[Vehicle]:
    vehicles = []
    for player in players.values():
        for vehicle in player.vehicleGroup:
            vehicles.append(vehicle)
    return vehicles
        


def find_vehicle(id: str, group = vesselGroup) -> Vehicle | None:
    for vehicle in group:
        # print('Vehicle Id', vehicle.id, 'Ours', id)
        if vehicle.id == id:
            return vehicle
    return None

def cleanup_objects():
    # Remove old fruits
    current_fruit_ids = {fruit.id for fruit in fruitGroup}
    for fruit in list(fruitGroup):
        if fruit.id not in current_fruit_ids:
            fruitGroup.remove(fruit)

    # Remove old vessels
    current_vessel_ids = {vessel.id for vessel in vesselGroup}
    for vessel in list(vesselGroup):
        if vessel.id not in current_vessel_ids:
            vesselGroup.remove(vessel)

    # Remove old vehicles
    for player in players.values():
        current_vehicle_ids = {v.id for v in player.vehicleGroup}
        for vehicle in list(player.vehicleGroup):
            if vehicle.id not in current_vehicle_ids:
                player.vehicleGroup.remove(vehicle)



def create_players(data: dict):
    global players, playerNum

    # Track existing player and vehicle IDs
    existing_player_keys = set(players.keys())
    current_fruit_ids = set(fruit.id for fruit in fruitGroup)
    
    # Loop through incoming data
    for key, playerData in data.items():
        num = playerData['playerNum']

        if key == playerId:
            playerNum = num

        # If player exists, update it
        if key in existing_player_keys:
            player = players[key]
            vessel = player.vessel
        else:
            # Create new player and vessel
            vessel = Vessel(
                VESSEL_FILENAMES[num],
                initPosition=[playerData['x'], playerData['y']],
                id=key,
                playerId=playerId
            )
            player = Player(key, pygame.sprite.Group(), vessel, num, color=playerData['color'])
            vesselGroup.add(vessel)
            players[key] = player

        # Update vessel and player information
        vessel.playerId = playerId
        player.score = playerData['score']
        vessel.rect.x = playerData['x']
        vessel.rect.y = playerData['y']
        vessel.dir = playerData['dir']

        # Handle fruits
        for id, fruitData in playerData.get('fruits', {}).items():
            if id not in current_fruit_ids:
                fruit = Fruit(
                    fruitData['initPosition'],
                    fruitData['initDir'],
                    fruitData['type'],
                    id
                )
                fruitGroup.add(fruit)
                current_fruit_ids.add(id)

        # Handle vehicles
        existing_vehicle_ids = {v.id for v in player.vehicleGroup}
        
        for vehicleData in playerData.get('vehicles', {}).values():
            id = vehicleData['id']
            if id in existing_vehicle_ids:
                # Update existing vehicle
                vehicle = next(v for v in player.vehicleGroup if v.id == id)
                vehicle.external_update(vehicleData)
                # print(f'Updated vehicle {id} for player {key}')
            else:
                # Create new vehicle if allowed
                if len(player.vehicleGroup) < N_VEHICLES:
                    vehicle = Vehicle(
                        VEHICLE_FILENAMES[player.playerNum],
                        key,
                        vehicleData['ksi'],
                        vehicleData['lat'],
                        vehicleData.get('speedUpdate', VESSEL_SPEED_UPDATE),
                        id=id,
                        playingId=playerId
                    )
                    player.vehicleGroup.add(vehicle)
                    print(f'Added vehicle {id} for player {key}')
                else:
                    print(f'Cannot add vehicle {id} for player {key}: max vehicles reached')

        # Remove vehicles not in the incoming data
        incoming_vehicle_ids = {v['id'] for v in playerData.get('vehicles', {}).values()}
        for vehicle in list(player.vehicleGroup):
            if vehicle.id not in incoming_vehicle_ids:
                player.vehicleGroup.remove(vehicle)
                print(f'Removed vehicle {vehicle.id} for player {key}')
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
    fruitGroup.empty()
    vesselGroup.empty()
    players = {}
    playerId = data['id']
    
    create_stars()

    players_data = data['players']
    create_players(players_data)
    # create_vehicles()
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
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sio.disconnect()

    # Clear the screen
    window.fill(BLACK)
    
    # Draw background
    window.blit(background, background.get_rect())

    # Update time
    currentTime = time.time()
    
    # Update and draw stars
    for star in stars:
        star.update()
        star.draw(window)

    if phase == 1:  # Waiting phase
        text = display_font_2.render('Waiting for more players to join...', True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
        window.blit(text, text_rect)
        
    elif phase == 2:  # Race phase
        pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BANNER_HEIGHT))
        # Display race timer
        raceTimer = display_font_3.render(str(int(RACE_DURATION + startTime - currentTime)), True, YELLOW)
        text_rect = raceTimer.get_rect(center=(WINDOW_WIDTH / 2, 30))
        window.blit(raceTimer, text_rect)

    elif phase == 3 and winner:  # Post-game phase
        pygame.draw.rect(window, BLACK, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BANNER_HEIGHT))
        raceTimer = display_font_3.render('0', True, YELLOW)
        text_rect = raceTimer.get_rect(center=(WINDOW_WIDTH / 2, 30))
        window.blit(raceTimer, text_rect)
        winner_player = players[winner['id']]
        winnerText = display_font_2.render('Player ' + str(winner_player.playerNum) + ' wins!', True, winner_player.color)
        text_rect = winnerText.get_rect(center=(WINDOW_WIDTH / 2, 0.35 * WINDOW_HEIGHT))
        window.blit(winnerText, text_rect)

    if phase >= 2:
        # Update all sprites
        fruitGroup.update()
        vesselGroup.update()
        for player in players.values():
            player.vehicleGroup.update()
        
        # Draw all sprites
        fruitGroup.draw(window)
        vesselGroup.draw(window)
        for player in players.values():
            player.vehicleGroup.draw(window)

        # Update and draw progress bars
        for key, player in players.items():
            playerNum = player.playerNum
            name = 'Player ' + str(playerNum)
            bar, bar_im, bar_pos = player.createProgressBar()
            positions = [
                (5, 5), 
                (window.get_width() - bar.get_width() - 5, 5),
                (5, window.get_height() - bar.get_height() - 5), 
                (window.get_width() - bar.get_width() - 5, window.get_height() - bar.get_height() - 5)
            ]
            window.blit(bar, positions[playerNum])
            bar_pos.x = player.score / track.maxRaceLength * PROGRESS_BAR_SIZE[0]
            lap = ' lap' if player.score <= 1.0 else ' laps'
            playerProgress = 'Player ' + name + ': ' + str("{:.2f}".format(player.score)) + lap
            window.blit(display_font_4.render(playerProgress, True, player.color), positions[playerNum])
    
    # Refresh display
    pygame.display.flip()
    clock.tick(FPS)

    if phase == 2 and winner and RACE_DURATION + startTime - currentTime <= 1.0:
        for player in players.values():
            for vehicle in player.vehicleGroup:
                vehicle.speedUpdate = [0, vehicle.speed, 0.0, VEHICLE_SPEED_PARAMS[5], 1]

pygame.quit()
