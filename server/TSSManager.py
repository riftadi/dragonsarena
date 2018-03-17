import json
import time
import sys
from threading import Thread

from server.TSSModel import TSSModel

class TSSManager(Thread):
    """
        This class is responsible to maintain all TSS states
        in the TSS model class. The execution of commands in
        the trailing states is the main task of this class.
    """
    def __init__(self, tss_model, message_box):
        Thread.__init__(self)
        self.tss_model = tss_model
        self.message_box = message_box

        self.trailing1_delay = 200

        self.trailing1_execution_time = 0

    def run(self):
        while self.tss_model.is_game_running():
            curr_time = self.tss_model.get_current_time()

            if curr_time >= self.trailing1_delay:
                # execute trailing1 state actions
                trailing1_gametime = curr_time - self.trailing1_delay
                action_list = self.message_box.get_messages_within_timestamp(self.trailing1_execution_time, trailing1_gametime)

                is_consistent = True

                # check if all action in action list is in leadingstate
                for action in action_list:
                    if not self.tss_model.get_leadingstate().is_action_id_exist(action["msg_id"]):
                        # action does not exist, there is inconsistency!
                        is_consistent = False
                        break

                if not is_consistent:
                    sys.stdout.flush()
                    print "inconsistencies detected!!"
                    # there is inconsistency detected
                    # duplicate first trailing state to leading state
                    self.tss_model.copy_trailing_to_leading_state()
                    # get the complete action list until current time
                    action_list_until_curr_time = self.message_box.get_messages_within_timestamp(self.trailing1_execution_time, curr_time)
                    # execute all actions until current time to leading state
                    self.tss_model.process_action_list(action_list_until_curr_time, state_id=0)

                # let's execute the action list in the trailing state
                self.tss_model.process_action_list(action_list, state_id=1)

                # update trailing state 1 execution time
                self.trailing1_execution_time = curr_time

            time.sleep(200.0/1000.0)

