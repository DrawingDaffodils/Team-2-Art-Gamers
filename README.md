# Team 2 Art Gamers
 
Name:
Fruit ans Rockets

Desription:
Fruit and Rockets is a multi-player game written in python where the players
can shoot fruit at opponents' rockets in order to slow them down so that
the person with the most hits can cross the finish line first.

Installation:

Before you can play, you need to do the following pip installs:

pip install pygame pillow aiohttp python-socketio python-socketio[client]

After `pip linstall`, download the following repository using the following:
 
 `git clone https://github.com/DrawingDaffodils/Team-2-Art-Gamers`

After sucessfully cloning the repo, run `cd Team-2-Art-Gamers`

Next, change the branch using the following:

`git checkout refactoring`

# Runnning the game:

## running on the Pi server:

Run `python main.py` file

## Running server on your commputer:
1. Open [constants.pi](constants.pi) and change `SOCKETIO_URL` to `http://localhost:9000`

2. Run `python server.py`

3. Run `python main.py` in two different terminals.