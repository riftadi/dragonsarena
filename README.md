# Dragons Arena: Warriors vs Dragons RTS Game

Dragons Arena is online warfare game between computer-controlled dragons and hundreds of virtual knights (avatars or real-life humans).
This game is developed as an labwork assignment in [TU Delft's](https://www.tudelft.nl/) IN4391 *Distributed Computing Systems* course. The course is/was scheduled in Q3 of academic year 2017/18.

Dragons Arena employs Trailing State Synchronization [^1] algorithm to synchronize action messages between peer-to-peer servers.

The basic design of this game is depicted in the following image.

![Classes design of Dragons Arena](https://github.com/riftadi/dragonsarena/raw/master/da_design.png)

[^1] Eric Cronin, Burton Filstrup, Anthony R. Kurc, and Sugih Jamin, An efficient synchronization mechanism for mirrored game architectures, NETGAMES, 2002.

# Client --> Server Communication
## Spawn Action
When a client joins the game he sends a spawn message with his client id. The id is uuid v4 and therefore random. On the server side, the character gets added to the gameboard with the initial coordinates.

```json
{
    "type" : "spawn",
    "player_id" : "uuid4 in hex format",
    "player_type" : "human or dragon"
}
```

## Heal Action
A human player can help a nearby friend by healing him. For that the id of the friend is needed.

```json
{
    "type" : "heal",
    "player_id" : "client uuid",
    "target_id" : "friend uuid",
}
```

## Move Action
Human players can move on the gameboard. The client proposes the new coordinates and the server validates the move.

```json
{
    "type" : "move",
    "player_id" : "client uuid",
    "x" : "new x coordinate",
    "y" : "new y coordinate"
}
```

## Attack Action
Both human and dragons can attack the counter character type each turn.

```json
{
    "type" : "attack",
    "player_id" : "client uuid",
    "target_id" : "enemy uuid",
}
```

# Server --> Server and Server --> Client communication
The communication between Server and Server plus Server and Client uses the publish/subscribe pattern. The Server published messages with different topics and the subscriber can decide to which topic to listen

## topic: gamestate
The gameengine publishes the current gamestate in a json format every iteration. For that the current list of alive players is published. The client listens to this event and creates a new game state out of this information and updates the bot plus the graphical user interface (gui).

```json
[{
    "x": "x coordinate of player",
    "y": "y coordinate of player",
    "hp": "current amount of health points",
    "max_hp": "",
    "type": "h(uman) or d(ragon)",
    "id": "player uuid"
}]
```
## topic: gameover
Notifies interested subscriber that the current played game is over. Clients listen to it to shutdown the game.

## topic: command
When a server receives a command from the client it immediatly pubilshes it with the topic ```command```. It adds the ```timestamp``` property to the JSON message that the other server can sort it within there TSS engine.

```json
{
    "timestamp": "local progress",
    ...
}
```

## topic: alive
send a heartbeat once in the gameloop to tell the other servers that oneself is alive. Other server can declare one as dead and therefore are not waiting a response for the commit process for spawning and starting time of the game.
{
    "id": "server adress,
    "time: "current gametime"
    
}

## topic: spawn
Use a two phase commit for making sure that a player can spawn safely. The server who has a client which wants to spawn get's coordinates for new player and locks is locally (means that a move coordinate to this coordinate is refused). It afterwards proposes these coordinates to all other players and waits a vote message of them in order to commit it afterwards. As soon as there is one abort it tries a new coordinate.

It may be that we can don't need the last commit message as all servers a listen to the vote anyway (or we use one to one messages for that). The heartbeat (alive topic) can be used to know for how many vote messages to wait.

```
{
    "phase": "proposal",
    "id": "id of new player",
    "type: "human or dragon",
    "x": "proposed x coordinate",
    "y": "proposed y coordinate"
}
```

```
{
    "phase": "vote",
    "id": "vote in favour of coordinates for new player with id"
}
```

```
{
    "phase": "abort",
    "id": "vote against coordinates for new player with id"
}
```

```
{
    "phase": "commit",
    "id": "commit new coordinates for player with id"
}
```

## topic start
Server have to agree on a timestamp on which the counter of the gametime is based on. It does not matter if there is a certain small delta between the servers.
- leader (defined before start) sends out his timestamp and the others adapt to it
- everyone waits till it receives a heartbeat from all other servers and then sends out his timestamps (the youngers one get's selected)
- some voting
# Usage

For starting the server component

```
python Server.py
```

For starting a bunch of dragon and human bots plus an additional bot with gui

```
./battle.sh
```

Other than that, to start an observer manually we can use this command:
```
python -m client.Observer <publisher_url>
ex:
python -m client.Observer 127.0.0.1:8181
```

To start a human player manually:
```
python -m client.run_client <publisher_url> <command_url>
ex:
python -m client.run_client 127.0.0.1:8181 127.0.0.1:8282
```

To start a dragon player manually:
```
python -m client.run_client <publisher_url> <command_url> dragon
```
