#!/usr/bin/python
import time
import pygame
import sys
import zmq
import uuid

from Bot import HumanBot, DragonBot
from Character import *
from UnifiedMessageBox import UnifiedMessageBox
from GUIDisplay import GUIDisplay

from json_encoder import GameStateParser

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:4999")
subscriber.setsockopt(zmq.SUBSCRIBE, "gamestate")
subscriber.setsockopt(zmq.SUBSCRIBE, "game over")

msg_box = UnifiedMessageBox()
player_id = uuid.uuid4().hex

player_type = "human"
display_delay = 0

gui = None

if len(sys.argv) == 2:
    player_type = sys.argv[1]

if len(sys.argv) == 3:
    gui = GUIDisplay(display_delay)
    gui.start()
# spawn
msg = {
    "type" : "spawn",
    "player_id" : player_id,
    "player_type" : player_type
}

msg_box.send_message(msg)

bot = HumanBot(player_id,msg_box)

bot.start()

if len(sys.argv) == 3:
    player_type = sys.argv[1]

while not bot.is_done():
    [topic, messagedata] = subscriber.recv_multipart()

    if topic == "game over":
        break

    parser = GameStateParser()
    gamestate = parser.parse(messagedata)
    bot.update_gamestate(gamestate)

    if gui is not None:
        gui.set_gamestate(gamestate)

subscriber.close()
context.term()
if gui is not None:
    gui.stop()
    gui.join()

bot.join()