import json
import logging
import time
import uuid
from threading import Thread

from server.TSSModel import TSSModel
from common.settings import *

class TSSManager(Thread):
    """
        This class is responsible to maintain all TSS states
        in the TSS model class. The execution of commands in
        the trailing states is the main task of this class.
        It also checks for stale players and respond accordingly.
    """
    def __init__(self, tss_model, message_box, server_command_duplicator, server_id, absolute_game_start_time):
        Thread.__init__(self)
        self.tss_model = tss_model
        self.message_box = message_box
        self.server_command_duplicator = server_command_duplicator
        self.absolute_game_start_time = absolute_game_start_time
        self.server_id = server_id

        self.trailing1_delay = TRAILING_01_DELAY
        self.start_checking_flag = False
        self.stale_counter = 0

        now = int(round(time.time() * 1000))
        self.trailing1_execution_time = now

        # self.trailing1_event_time = 0

    def run(self):
        while self.tss_model.is_game_running():
            now = int(round(time.time() * 1000))
            if not self.start_checking_flag:
                if now >= self.absolute_game_start_time + self.trailing1_delay:
                    # it is trailing state 1's time to start checking
                    self.start_checking_flag = True
            else:
                self.execute_state(state_id=TRAILING_01_STATE, curr_time=now)

            if self.stale_counter % 5 == 4:
                self.manage_stale_players()
            self.stale_counter += 1
            
            time.sleep(float(self.trailing1_delay)/1000.0)

    def execute_state(self, state_id, curr_time):
        action_list = []

        if state_id == TRAILING_01_STATE:
            # check for inconsistency in trailing state
            tss1_action_list = self.message_box.get_unchecked_messages_within_timestamp(self.trailing1_execution_time, curr_time)

            # check if all action in action list is in state
            is_consistent = self.check_consistency(tss1_action_list)

            if not is_consistent:
                # there is inconsistency detected
                incmsg = "Inconsistency detected!! Duplicating trailing state.."
                print incmsg
                logging.info(incmsg)

                # repair our leadingstate
                # rollback to trailing01 state and re-executes commands until current time
                full_action_list = self.message_box.get_all_unchecked_messages_for_rollback_from_timestamp(self.trailing1_execution_time)

                # for debugging purpose
                # print "tss1_actions: %s" % str(tss1_action_list)
                # print "applying_to_leading: %s" % str(full_action_list)

                self.tss_model.rollback_state(command_list=full_action_list)

        if state_id == TRAILING_01_STATE:
            if (len(tss1_action_list) > 0):
                # execute the action list in the state, if there are some
                self.tss_model.process_action_list(tss1_action_list, state_id=state_id)
                # delete checked messages for TSS1
                self.message_box.delete_trailingstate1_checked_messages()

            # update trailing state 1 execution time
            self.trailing1_execution_time = curr_time

    def check_consistency(self, action_list):
        consistent_flag = True
        leading_executed_msg_ids = self.tss_model.get_leadingstate().get_executed_msg_ids()

        trailing_msg_ids = []
        for action in action_list:
            trailing_msg_ids.append(action["msg_id"])

        # for debugging purpose
        # print "t:%s" % str(trailing_msg_ids)
        # print "l:%s" % str(leading_executed_msg_ids)

        if len(trailing_msg_ids) > 0:
            # find the offset
            offset = 0
            offset_max = len(leading_executed_msg_ids)

            try:
                while offset < offset_max:
                    if leading_executed_msg_ids[offset] != trailing_msg_ids[0]:
                        offset += 1
                    else:
                        break

                if offset == offset_max:
                    consistent_flag = False
                else:
                    for i in xrange(len(trailing_msg_ids)):
                        if RELAX_TSS_ORDER_CHECKING:
                            if not trailing_msg_ids[i] in leading_executed_msg_ids:
                                consistent_flag = False
                                break
                        else:
                            if leading_executed_msg_ids[offset+i] != trailing_msg_ids[i]:
                                consistent_flag = False
                                break
            except:
                consistent_flag = False

        return consistent_flag

    def manage_stale_players(self):
        unactive_player_ids = self.tss_model.get_unactive_player_ids()

        if len(unactive_player_ids) > 0:
            for unpid in unactive_player_ids:
                offmsg = "player %s offline, saving state.." % unpid
                print offmsg
                logging.info(offmsg)
                msg = {}
                msg["player_id"] = unpid
                msg["type"] = "off"

                # increment lamport clock
                self.tss_model.increase_event_clock()

                # add lamport clock to our message
                msg["eventstamp"] = self.tss_model.get_event_clock()
                # add local clock to our message
                msg["timestamp"] = int(round(time.time() * 1000))
                # seed the msg_id with our server_id so that it is unique globally
                msg["msg_id"] = uuid.uuid1(self.server_id).hex
                msg["server_id"] = self.server_id

                # save the command for state duplication purposes
                self.message_box.put_message(msg)

                # execute the command right away in the leading state
                self.tss_model.process_action(msg, state_id=LEADING_STATE)
                
                # duplicate command to peers
                self.server_command_duplicator.publish_msg_to_peers(msg)
