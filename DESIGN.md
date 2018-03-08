# Dragons Arena Design Document

![Image of Architecture](architecture.png)

# Client
## Dragon/Human
- chose randomly one server as there main connection to the game
- listen to the publisher of that server
- topic alive: if the no answer for two long switch over to another server
- has unique id which does not change after restart (may be uuid written to file)
- sends spawn message after start
- runs bot
- but starts sending commands once it sees it's own id in the received gamestate

## GUI
- chose one server for gamestate
- renders gamestate and closes gui after receiving game over state

# Server
- after server startup it tries to commit to one chosen beginning timestamp from which the internal clock starts 
- has one publisher (for possible commands see [README.md](README.md))
- has one server for receiving commands of connected clients (connection is stateless)
- when receiving a normal command (except spawn). Tag it with internal clock and publishes it. 
- has message buffer which is emptied after the TSS if in the past
- has a TSS engine which runs the game with a difference of 100ms each
- has spawning component which runs outside the TSS engine and looks for a free spot in the leading state and proposes this to the others. This component buffers the spawning messages till it has chosen a start time.

## handling server fault
- server publishes heartbeat per gameloop
- if the other server don't hear anything for a certain time they exclude the server from voting for new

- on server restart the server waits for the heartbeats of other servers, when one has a valid timestamp then it know that he was down.
- has to queue all messages it listens from the other server till it got the past gamestate of the other server
  - either get a copy of the gamestate
  - or get the history of all commands and make a replay
