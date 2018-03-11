import time
from threading import Thread

from server.TSSModel import TSSModel

class GameClockManager(Thread):
    """
        This class is responsible to advance the game timer,
        do winning condition checking in the main TSSModel,
        and clearing message box(es) every 500 ms.
    """
    def __init__(self, tss_model, message_box, update_delay=10.0):
        Thread.__init__(self)
        self.tss_model = tss_model
        self.message_box = message_box
        self.update_delay = float(update_delay)

    def run(self):
        while self.tss_model.is_game_running():
            # advancing game clock
            self.tss_model.advance_game_time_by(self.update_delay)

            # every 300 ms check winning condition
            if (self.tss_model.get_current_time() % 300 == 0):
                self.tss_model.check_game_end_condition()

            # clear message_box every 500 ms
            current_time = self.tss_model.get_current_time()
            if (current_time % 500 == 0):
                self.message_box.delete_messages_before(current_time)

            time.sleep(self.update_delay/1000.0)
