import json
import time
from threading import Thread

from server.TSSModel import TSSModel

class TSSManager(Thread):
    """
        This class is responsible to maintain all TSS states
        in the TSS model class. The execution of commands in
        the trailing states is the main task of this class.
    """
    def __init__(self, tss_model, message_box, absolute_game_start_time):
        Thread.__init__(self)
        self.tss_model = tss_model
        self.message_box = message_box
        self.absolute_game_start_time = absolute_game_start_time

        self.trailing1_delay = 400
        self.start_checking_flag = False

        now = int(round(time.time() * 1000))
        self.trailing1_execution_time = now

        # self.trailing1_event_time = 0

    def run(self):
        while self.tss_model.is_game_running():
            now = int(round(time.time() * 1000))
            if not self.start_checking_flag:
                if now >= self.absolute_game_start_time + self.trailing1_delay:
                    # it is our time to start checking
                    self.start_checking_flag = True
            else:
                self.execute_state(state_id=1, curr_time=now)

            time.sleep(float(self.trailing1_delay)/1000.0)

    def execute_state(self, state_id, curr_time):
        action_list = []

        if state_id == 1:
            # check for inconsistency in trailing state
            action_list = self.message_box.get_unchecked_messages()

            # check if all action in action list is in state
            is_consistent = self.check_consistency(action_list)

            if not is_consistent:
                # there is inconsistency detected
                print "inconsistency detected!! duplicating trailing state.."

                # repair our leadingstate
                # rollback to previous state and reexecutes commands
                command_list = self.message_box.get_messages_within_timestamp(self.trailing1_execution_time, curr_time)
                self.tss_model.prepare_rollback(command_list=command_list)
                last_time = curr_time
                now = int(round(time.time() * 1000)) + 10000
                command_list = self.message_box.get_messages_within_timestamp(last_time, now)
                self.tss_model.rollback_state(command_list=command_list)

        if (len(action_list) > 0):
            # execute the action list in the state
            self.tss_model.process_action_list(action_list, state_id=state_id)

        if state_id == 1:
            # update trailing state 1 execution time
            self.trailing1_execution_time = curr_time

    def check_consistency(self, action_list):
        consistent_flag = True
        leadingstate = self.tss_model.get_leadingstate()

        msg_id_list = []
        for action in action_list:
            msg_id_list.append(action["msg_id"])

        for msg_id in msg_id_list:
            if not leadingstate.is_action_id_exist(msg_id):
                # msg_id does not exist, there is inconsistency!
                consistent_flag = False
                break

        return consistent_flag
