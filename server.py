import time
from aiohttp import web
from constants import *  # Ensure constants are correctly defined
import socketio
import random
from objects import track
import asyncio
from uuid import uuid4

# Create websocket server
ws = socketio.AsyncServer()
# Create http server
app = web.Application()

# Connect WebSocket server to HTTP server
ws.attach(app)

players = {}
tick_count = 0
tick_interval = 24 # Number of ticks per second (adjust as needed)
ticker_started = False
ticker_task = None
race_start_time = None


def update_vehicle_state(vehicle):
    # Extracting vehicle attributes
    speed = vehicle['speed']
    ksi = vehicle['ksi']
    lat = vehicle['lat']
    seg = vehicle['seg']
    lap = vehicle['lap']
    distance = vehicle['distance']
    speedUpdate = vehicle['speedUpdate']
    latUpdate = vehicle['latUpdate']
    lastHit = vehicle.get('lastHit', 0)
    hit = vehicle.get('hit', False)
    
    # Temporary state for computations
    temp_speed = speed
    temp_ksi = ksi
    temp_lat = lat
    temp_seg = seg
    temp_lap = lap
    temp_distance = distance if lap >= 1 else 0

    # Update speed
    if speedUpdate[4] == 0:  # Not being forced to stop
        if speedUpdate[0] == 0:  # Speed is not being updated
            if random.random() < VEHICLE_SPEED_PARAMS[1]:
                startSpeed = temp_speed
                endSpeed = random.uniform(VEHICLE_SPEED_PARAMS[2], VEHICLE_SPEED_PARAMS[3]) * VEHICLE_SPEED_PARAMS[0]
                accelRatio = random.uniform(VEHICLE_SPEED_PARAMS[4], VEHICLE_SPEED_PARAMS[5])
                speedUpdate = [1, startSpeed, endSpeed, accelRatio, 0]
        if speedUpdate[0] == 1:  # Speed is being updated
            if time.time() - lastHit >= 5:
                temp_speed += speedUpdate[3] * (speedUpdate[2] - speedUpdate[1])
                if ((speedUpdate[2] - speedUpdate[1] >= 0) and (temp_speed >= speedUpdate[2])) or ((speedUpdate[2] - speedUpdate[1] < 0) and (temp_speed <= speedUpdate[2])):
                    temp_speed = speedUpdate[2]
                    speedUpdate = [0, 0, 0, 0, 0]

    else:  # being forced to stop
        temp_speed += speedUpdate[3] * (speedUpdate[2] - speedUpdate[1])
        if temp_speed <= speedUpdate[2]:
            temp_speed = 0.0

    # Handle hit
    if hit:
        time_since_hit = time.time() - lastHit
        if time_since_hit < 5:  # 5 seconds after hit
            temp_speed *= 0.55

    # Update lateral position
    if speedUpdate[4] == 0:  # Not being forced to stop
        if latUpdate[0] == 0:  # Lateral position not being updated
            if random.random() < VEHICLE_LAT_PARAMS[1]:
                startLat = temp_lat
                endLat = random.uniform(-VEHICLE_LAT_PARAMS[0], VEHICLE_LAT_PARAMS[0])
                accelRatio = random.uniform(VEHICLE_LAT_PARAMS[2], VEHICLE_LAT_PARAMS[3])
                latUpdate = [1, startLat, endLat, accelRatio]
        if latUpdate[0] == 1:  # Lateral position being updated
            temp_lat += latUpdate[3] * (latUpdate[2] - latUpdate[1])
            if ((latUpdate[2] - latUpdate[1] >= 0) and (temp_lat >= latUpdate[2])) or (latUpdate[2] - latUpdate[1] < 0) and (temp_lat <= latUpdate[2]):
                temp_lat = latUpdate[2]
                latUpdate = [0, 0, 0, 0]

    # Update position on the track
    distanceToCover = temp_speed
    if track.segTypes[temp_seg] == 2:  # If the segment is an arc
        segPlusOne = (temp_seg + 1) % track.nSeg  # Next segment
        trackWidth = track.transPoints[temp_seg][2] + temp_ksi * (track.transPoints[segPlusOne][2] - track.transPoints[temp_seg][2])  # Track width
        distanceToCover = distanceToCover * track.arcData[temp_seg][2] / (track.arcData[temp_seg][2] - track.arcOrient[temp_seg] * temp_lat * trackWidth / 2)
    while distanceToCover > 0:
        newKsi = temp_ksi + distanceToCover / track.segLen[temp_seg]
        if newKsi < 1:  # Still in the same segment
            if (temp_seg == 0 and temp_ksi < track.startKsi and newKsi >= track.startKsi):  # Update lap number
                temp_lap += 1
            temp_ksi = newKsi
            newCoords = natToGlobal(track, temp_seg, temp_ksi, temp_lat)
            temp_dir = newCoords[2]
            distanceToCover = 0
        else:  # Moving to the next segment
            distanceToCover -= track.segLen[temp_seg] * (1 - temp_ksi)
            temp_seg = (temp_seg + 1) % track.nSeg
            temp_ksi = 0.0

    # Calculate distance covered
    if lap >= 1 and speedUpdate[4] == 0:
        temp_distance += (temp_lap - lap) * track.trackLen - TRACK_KSI * track.segLen[0] + temp_ksi * track.segLen[temp_seg]
        for iSeg in range(temp_seg):
            temp_distance += track.segLen[iSeg]
        if temp_seg == 0 and temp_ksi < TRACK_KSI:
            temp_distance += track.trackLen

    vehicle.update({
        'seg': temp_seg,
        'ksi': temp_ksi,
        'lat': temp_lat,
        'speed': temp_speed,
        'dir': temp_dir,
        'distance': temp_distance,
        'lap': temp_lap,
        'x': newCoords[0],
        'y': newCoords[1],
        'speedUpdate': speedUpdate,
    })

    return vehicle

def create_vehicles():
    global players

    player_ids = list(players.keys())
    num_players = len(player_ids)

    # Default spacing values
    spacing = TRACK_STARTING_GRID[2]
    vehicles_per_row = TRACK_STARTING_GRID[0]

    # Create a list of vehicles for processing
    vehicles_to_create = N_VEHICLES * num_players

    ksi = track.startKsi - TRACK_STARTING_GRID[1]
    lat = 0
    if vehicles_per_row > 1:
        lat = -VEHICLE_LAT_PARAMS[0]

    for i in range(vehicles_to_create):
        player_id = player_ids[i % num_players]
        player = players[player_id]

        if len(player['vehicles']) >= N_VEHICLES:
            # Skip creating vehicles for this player if already has the maximum number
            continue

        # Default lateral positions and ksi
        id = uuid4().hex
        vehicle = {
            "id": id,
            "lat": lat,
            "ksi": ksi,
            "speedUpdate": [1, 0.00, random.randint(5, 8), VEHICLE_SPEED_PARAMS[5], 0],
            "speed": 0,
            "seg": 0,
            "lap": 0,
            "distance": 0,
            "latUpdate": [0, 0, 0, 0],
            # "lastHit": None,
            "hit": False
        }

        # Update ksi for the next vehicle
        ksi -= spacing
        if vehicles_per_row > 1:
            # Distribute vehicles evenly across rows
            row_index = i % vehicles_per_row
            lat = -VEHICLE_LAT_PARAMS[0] + (2 * row_index / (vehicles_per_row - 1)) * VEHICLE_LAT_PARAMS[0]

        players[player_id]['vehicles'][id] = vehicle

        # Optional: Additional setup for each vehicle, if needed
        # For example, adding vehicles to a sprite group or handling player-specific initialization

async def ticker():
    print('Ticker started')
    global tick_count, ticker_started, race_start_time
    
    while True:
        # if not ticker_started:
        #     await asyncio.sleep(1)  # Sleep for 1 second before checking again
        #     continue

        await asyncio.sleep(1 / tick_interval)  # Sleep for the appropriate fraction of a second
        tick_count += 1

        # print('Tick', tick_count)

        if race_start_time:
            elapsed_time = time.time() - race_start_time
            if elapsed_time >= RACE_DURATION:
                print('Calculating winner...')
                await calculate_winner()
                # Reset ticker
                race_start_time = None
                ticker_started = False
                continue
        
        for id, player in players.items():
            for key, vehicle in player['vehicles'].items():
                players[id]['vehicles'][vehicle['id']] = update_vehicle_state(vehicle)

        # Send player data to all clients
        await ws.emit('player_data', players)
        for player in players.values():
            # if len(player['fruits']) > 2:
            player['fruits'] = {}


@ws.on('update')
async def update(sid, data):
    '''
    Runs every time the 'update' event is emitted
    '''
    # Update player data
    if 'fruit' in data:
        fruitId = data['fruit']['id']


        if 'kill' in data['fruit']: # If data['fruit'] == {} and player['fruits] != []
            if fruitId in players[sid]['fruits']:
                del players[sid]['fruits'][fruitId] # Removes the fruit
        else:
            players[sid]['fruits'][fruitId] = data['fruit']


        del data['fruit'] # Deletes the fruit from dictionary
    
    if 'vehicle' in data:
        vehicleId = data['vehicle']['id']


        if 'kill' in data['vehicle']: # If data['vehicle'] == {} and player['vehicles] != []
            if vehicleId in players[sid]['vehicles']:
                del players[sid]['vehicles'][vehicleId] # Removes the vehicle
        else:
            players[sid]['vehicles'][vehicleId] = data['vehicle']


        del data['vehicle'] # Deletes the vehicle from dictionary
  
  
    players[sid].update(data)

@ws.on('collision')
async def collision(sid, data):
    print('collision', data)
    vehicle_id = data['vehicle_id']
    vehicle_owner = data['vehicle_owner']

    vehicle = players[vehicle_owner]['vehicles'][vehicle_id]
    # Lower vehicle speed for the next 5 ticks
    vehicle['lastHit'] = time.time()
    vehicle['hit'] = True
    

    players[vehicle_owner]['vehicles'][vehicle_id] = vehicle

@ws.event
async def connect(sid, environ):
    global ticker_started, race_start_time, players, ticker_task

    print("connect ", sid)
    playerNum = len(players)
    
    x, y = [WINDOW_WIDTH * ((1 - playerNum) * VESSEL_PARAMS[0] + playerNum * (1 - VESSEL_PARAMS[0])), WINDOW_HEIGHT * VESSEL_PARAMS[1]]
    players[sid] = {
        "playerNum": playerNum,
        "id": sid,
        "score": 0,
        "x": x, "y": y, "dir": 0,
        "color": random.choice(PLAYER_COLS),
        "fruits": {},
        "vehicles": {}
    }
    
    if len(players) > 1 and not ticker_started:
        ticker_started = True
        race_start_time = time.time()
        for id in players.keys():
            create_vehicles()
            await ws.emit('start', {"players": players, "startTime": time.time(), "id": id}, to=id)
        if ticker_task is None or ticker_task.done():
            print('Creating Lobby...')
            ticker_task = asyncio.create_task(ticker())
        

@ws.event
async def disconnect(sid):
    global ticker_started, ticker_task, race_start_time

    print('disconnect ', sid)
    if sid in players:
        del players[sid]  # Delete that player from the players dictionary
    if len(players) == 0:
        reset_game_state()
        

async def calculate_winner():
    global players
    if not players:
        return

    # Find the player with the highest score
    winner = max(players.values(), key=lambda p: p['score'])

    # Prepare the winner data
    winner_data = {
        'id': winner['id'],
        'score': winner['score'],
        'playerNum': winner['playerNum']
    }

    # Notify all clients of the winner
    await ws.emit('race_over', {'winner': winner_data})

    # Disconnect all clients
    for id in list(players.keys()):
        await ws.disconnect(id)

    # Optionally, reset the game state
    reset_game_state()

def reset_game_state():
    global players, ticker_started, tick_count, ticker_task
    print('Resetting lobby...')
    players = {}
    ticker_started = False
    if ticker_task:
        if ticker_task.cancel():
            print('Ticker stopped')
        else:
            print('Failed to stop ticker')
        ticker_task = None
    tick_count = 0

async def start_background_tasks(app):
    global ticker_task
    if ticker_task is None or ticker_task.done():
        ticker_task = asyncio.create_task(ticker())

async def cleanup_background_tasks(app):
    if ticker_task:
        ticker_task.cancel()
        await ticker_task

if __name__ == '__main__':
    # Start websocket server
    app.on_shutdown.append(cleanup_background_tasks)
    # app.on_startup.append(start_background_tasks)
    web.run_app(app)
