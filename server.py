from aiohttp import web
import socketio # Make sure to install the python-socketio package and NOT socketio

# Create websocket server
sio = socketio.AsyncServer()
# Create http server
app = web.Application()

# Connect Websocket server to http server (socket.io depends on it)
sio.attach(app)


players = {}

@sio.event
def connect(sid, environ):
    print("connect ", sid)
    players[sid] = { "playerNum": len(players) }

@sio.on('update')
async def update(sid, data):
    '''
    Runs every time the 'update' event is emitted (check line 170 in objects.py)
    '''
    print("message ", data)

    # Updates it x, y, and dir in the players 
    players[sid].update(data)
    print(sid, players[sid])

@sio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    web.run_app(app) # Start websocket server