import time
from aiohttp import web
from constants import *  # Ensure constants are correctly defined
import socketio
import asyncio

# Create websocket server
ws = socketio.AsyncServer()
# Create http server
app = web.Application()

# Connect WebSocket server to HTTP server
ws.attach(app)

players = {}
tick_count = 0
tick_interval = 24  # Number of ticks per second (adjust as needed)
ticker_started = False
ticker_task = None
race_start_time = None

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

        # Send player data to all clients
        await ws.emit('player_data', players)

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
  
    players[sid].update(data)

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
        "fruits": {}
    }
    
    if len(players) > 1 and not ticker_started:
        ticker_started = True
        race_start_time = time.time()
        await ws.emit('start', {"players": players, "startTime": time.time()})
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
