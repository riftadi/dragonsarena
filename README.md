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
    "type": "h(uman) or d(ragon)",
    "id": "player uuid"
}]
```
## topic: game over
Notifies interested subscriber that the current played game is over. Clients listen to it to shutdown the game.
# Usage

For starting the server component

```
python Server.py
```

For starting a bunch of dragon and human bots plus an additional bot with gui

```
./battle.sh
```
