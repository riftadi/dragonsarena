# Dragons Arena: Warriors vs Dragons RTS Game

Dragons Arena is online warfare game between computer-controlled dragons and hundreds of virtual knights (avatars or real-life humans).
This game is developed as an labwork assignment in [TU Delft's](https://www.tudelft.nl/) IN4391 *Distributed Computing Systems* course. The course is/was scheduled in Q3 of academic year 2017/18.

Dragons Arena employs Trailing State Synchronization [^1] algorithm to synchronize action messages between peer-to-peer servers.

The basic design of this game is depicted in the following image.

![Classes design of Dragons Arena](https://github.com/riftadi/dragonsarena/blob/master/da_design.png)

[^1] Eric Cronin, Burton Filstrup, Anthony R. Kurc, and Sugih Jamin, An efficient synchronization mechanism for mirrored game architectures, NETGAMES, 2002.
