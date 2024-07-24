from aiohttp import web
from constants import *
import socketio
import asyncio

# Create websocket server
sio = socketio.AsyncServer()
# Create http server
app = web.Application()

# Connect Websocket server to http server (socket.io depends on it)
sio.attach(app)

players = {}
tick_count = 0
tick_interval = 60  # Number of ticks per second (adjust as needed)

async def ticker():
    global tick_count
    while True:
        await asyncio.sleep(1 / tick_interval)  # Sleep for the appropriate fraction of a second
        tick_count += 1
        if tick_count >= tick_interval:
            tick_count = 0
            # Send player data to all clients
            await sio.emit('player_data', players)

@sio.event
def connect(sid, environ):
    print("connect ", sid)
    playerNum = len(players)
    x,y = [WINDOW_WIDTH * ((1 - playerNum) * VESSEL_PARAMS[0] + playerNum * (1 - VESSEL_PARAMS[0])), WINDOW_HEIGHT * VESSEL_PARAMS[1]]
    players[sid] = {
        "playerNum": playerNum,
        "id": sid,
        "score": 0,
        "x": x, "y": y, "dir": 0
    }

@sio.on('update')
async def update(sid, data):
    '''
    Runs every time the 'update' event is emitted
    '''
  
    # Update player data
    players[sid].update(data)
    print("message ", players[sid])
    

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    if sid in players:
        del players[sid] # Deletes that player from our players dictionary

async def start_background_tasks(app):
    asyncio.create_task(ticker())

async def cleanup_background_tasks(app):
    # Clean up tasks here if needed
    pass

if __name__ == '__main__':
    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(cleanup_background_tasks)
    
    # Start websocket server
    web.run_app(app)
