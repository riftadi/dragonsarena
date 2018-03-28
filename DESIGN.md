# Dragons Arena Design Document

![Image of Architecture](img/architecture.png)

![Classes design of Dragons Arena](img/da_design.png)


# Game Flow
## Client
### Dragon/Human
- chose randomly one server as their main connection to the game
- listen to the publisher of that server
- has unique id which does not change after restar
- sends spawn message after start
- runs bot
- starts sending commands once it sees it's own id in the received gamestate

### GUI/Observer
- chose one server for gamestate
- renders gamestate and closes gui after receiving game over state

## Server
- has two publisher (for possible commands see [README.md](README.md))
- has one server for receiving commands of connected clients (connection is stateless)
- when receiving a normal command (except spawn). Tag it with internal clock and publishes it. 
- has message buffer which is emptied after the TSS if in the past
- has a TSS engine which runs the game with a difference of 100ms each
- has spawning component which runs outside the TSS engine and looks for a free spot in the leading state and proposes this to the others. This component buffers the spawning messages till it has agreed on a spawning place.

# Fault tolerance

## Server fault
- server
    - a server which crashes can not come back 
    - server publishes heartbeat per gameloop
    - if the other server don't hear anything for a certain time they exclude the server from voting for new
- client
    - timeout for each command send
    - runs out means switching over to other server

## Client fault
- server
    - each client sends a new command with a time interval
    - when the server does not hear from a client it removes the player from the gameboard and put's it in a list
    - does a new spawn with the same id happens the old gamestate get's applied
- client
    - if still on the gameboard the bot just sends new commands
    - if it has been taken out the game
    - client stops publishing new commands
    - has to come back with same id to continue
    - bot continues proposing new commands once it sees 


# Client --> Server Communication
## Spawn Action
When a client joins the game he sends a spawn message with his client id. The id has to be unique over the game. On the server side, the character gets added to the gameboard with the initial coordinates.

```json
{
    "type" : "spawn",
    "player_id" : "unique id",
    "player_type" : "human or dragon"
}
```

## Heal Action
A human player can help a nearby friend by healing him. For that the id of the friend is needed.

```json
{
    "type" : "heal",
    "player_id" : "client unique id",
    "target_id" : "friend unique id",
}
```

## Move Action
Human players can move on the gameboard. The client proposes the new coordinates and the server validates the move.

```json
{
    "type" : "move",
    "player_id" : "client unique id",
    "x" : "new x coordinate",
    "y" : "new y coordinate"
}
```

## Attack Action
Both human and dragons can attack the counter character type each turn.

```json
{
    "type" : "attack",
    "player_id" : "client unique id",
    "target_id" : "enemy unique id",
}
```

# Server --> Server and Server --> Client communication
The communication between Server and Server plus Server and Client uses the publish/subscribe pattern. The Server published messages with different topics and the subscriber can decide to which topic to listen

The server has two publishers one for the gamestate directed to the client and another one for the server to server communication.

## gamestate
The gameengine publishes the current gamestate in a json format every iteration. For that the current list of alive players is published. The client listens to this event and creates a new game state out of this information and updates the bot plus the graphical user interface (gui).

```json
[{
    "x": "x coordinate of player",
    "y": "y coordinate of player",
    "hp": "current amount of health points",
    "max_hp": "maximal amount of health points",
    "type": "h(uman) or d(ragon)",
    "id": "player unique id"
}]
```

## topic: command
When a server receives a command from the client it immediatly pubilshes it with the topic ```command```. It adds the ```timestamp``` property to the JSON message that the other server can sort it within there TSS engine.

```json
{
    "timestamp": "local progress",
    "type": "<heal, attack, move>"
}
```

## topic: alive
send a heartbeat once in the gameloop to tell the other servers that oneself is alive. Other server can declare one as dead and therefore are not waiting a response for the commit process for spawning and starting time of the game.

```json
{
    "id": "server adress",
    "time": "current gametime"
    
}
```

## topic: spawn
It uses a two-phase commit for making sure that a player can spawn safely. The server who has a client which wants to spawn get's coordinates for a new player and locks it locally (means that a move to this coordinate is refused). It afterwards proposes these coordinates to all other players and waits for a vote message of them in order to commit it afterwards. As soon as there is one abort it tries a new coordinate.

The spawn can be for a client which connects for the first time or respawns with it's previous amount of hp.
```json
{
    "type": "proposal",
    "player_id": "unique id of new player",
    "player_type": "human or dragon",
    "x": "proposed x coordinate",
    "y": "proposed y coordinate",
    "hp": "current hp of new character",
    "max_hp": "hp of new character",
    "ap": "ap of new character"
}
```

```json
{
    "type": "vote",
    "vote": "yes or no (bool)",
    "player_id": "new player id"
}
```

```json
{
    "type": "commit",
    "success": "bool indicates commit or rollback",
    "player_id": "new player id",
    "timestamp": "new time for TSS in other server",
    "eventstamp": "new event time for TSS in other server"
}
```

# Modules Organization

The source codes are organized following Python module packages structure. They are organized into 4 main directories:
1. common
2. server
3. client
4. img

![Classes design of Dragons Arena](img/da_design.png)

## common

This directory is used to store modules that are used both by server and client.

### Character, Human, and Dragons

These classes are reprentations of the characters in the game. Their important properties are: type (human or dragon), HP, max HP, AP, and location (x,y).

### GameBoard

This class stores the 25x25 game board grids state. The characters' objects are referred from the grids.

### GameState

This class stores gameboard and also the characters involved in a game. The GameState should always know how many players are still alive. If needed, this class can also contain the offline players list data.

### settings

This file contains all global constants and configurations. All hardcoded values should go here for easy maintainability.

### JSONEncoder

This class functions to serialize and deserialize GameState object to JSON format.

### SocketWrapper

This class functions to "wrap", i.e. enhance, `recv()` function in ZeroMQ to raise a timeout error.

## server

This directory is used to store server related modules. The modules in this class are described in the following subsections.

### Modeller Classes

#### TSSModel

TSSModel is a class responsible to contain:
* all gamestates,
* is_game_running flag,
* start time from epoch in milliseconds, and,
* running game clock.

In this class, the actual representation of three game states (leading, trailing01, and trailing02) of GameState object is stored. This class should not do any work by itself, and is only modified by server's controller/worker classes.

#### ClientMessageBox

This class is used to store messages coming from clients and peer servers to be used at later time by other classes.

### Controller/worker Classes

#### Server

This class is the container class for all modeller and worker classes in the server module. It initializes them and wait until the game is finished.

#### GameClockManager

This class is responsible to advance the gameclock every 10ms, do winning condition checking in the TSSModel every 300ms, and clearing ClientMessageBox every 500 ms.

#### GameStatePublisher

This class is responsible to broadcast the gamestates and game running state to the clients and observers connected to it. It creates a ZeroMQ PUB queue, reads the gamestate from the TSSModel, and put the gamestates into the queue every 300ms.

#### ClientCommandManager

This class creates a ZeroMQ REP and waits for action commands from the clients. If it receives action commands from any clients, it will give an ack to the client, send the command to ServerCommandDuplicator (which in turn will distribute the command to server peers), execute the command in the leading state, and save the commands in the ClientMessageBox instance. It should do all checking if a command is valid or not.

#### ServerCommandDuplicator

This class is responsible to duplicate commands received from the clients to peer servers and execute commands received from the peer servers in the TSSModel.

#### TSSManager

This class is responsible for TSS state checking and rollback management. Currently, there is only one trailing state implemented. It also checks for stale players and respond accordingly.

## client

This directory is used to store client related modules.

### Modeller Classes

There is no modeller class in this modules, *the client should be strictly stateless*.

### Controller/worker Classes

#### Client

This class as a container for other client classes and also instantiates the GameStateUpdater and ClientSideCommandSender. After that, it only waits until the game running state (which is periodically updated by GameStateUpdater) is finished.

#### Bots

This class reads the gamestate from GameStateUpdater, calculate next move, and finally send the action command via ClientSideCommandSender.

#### ClientSideCommandSender

This class is responsible to send the commands from bot to the server. The corresponding class in server is the ClientCommandManager class.

#### GameStateUpdater

This class read message published by the server via ZeroMQ SUB queue and update the gamestate accordingly.

#### GUIDisplay

This class reads the gamestate from GameStateUpdater and displays it to screen using pygame screen. The GUI should run in the main process and not on thread (otherwise it will crash in MacOS).

#### Observer

This class simply instantiate GUIDisplay.

## img

This directory is to store images only, whether for documentation or used in game.

