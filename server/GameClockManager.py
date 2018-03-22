import time
from threading import Thread

from server.TSSModel import TSSModel
from common.settings import *

class GameClockManager(Thread):
    """
        This class is responsible to advance the game timer,
        do winning condition checking in the main TSSModel,
        and clearing message box(es) every 500 ms.
    """
    def __init__(self, tss_model, message_box, update_delay=GAMECLOCK_UPDATE_DELAY):
        Thread.__init__(self)
        self.tss_model = tss_model
        self.message_box = message_box
        self.update_delay = float(update_delay)

    def run(self):
        while self.tss_model.is_game_running():
            # advancing game clock
            self.tss_model.advance_game_time_by(self.update_delay)

            current_time = self.tss_model.get_current_time()

            # every 300 ms check winning condition
            if (current_time % GAME_WINNING_CONDITION_CHECK_DELAY == 0):
                self.tss_model.check_game_end_condition()

            # clear message_box every 2000 ms
            if (current_time % CLEAR_MESSAGE_BOX_DELAY == 0):
                self.message_box.delete_checked_messages()

            time.sleep(self.update_delay/1000.0)
