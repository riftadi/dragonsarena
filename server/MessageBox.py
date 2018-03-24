import zmq
import json
from operator import itemgetter

class MessageBox(object):
    def __init__(self):
        self.message_box = []
        self.pending_commands = []
        self.server_id = 1
        self.msg_counter = 1

    def get_list_len(self):
        return len(self.message_box)

    # def delete_messages_before(self, time):
    #     new_msg_list = []
    #     for msg in self.message_box:
    #         if msg["timestamp"] >= time:
    #             new_msg_list.append(msg)
    #     self.message_box = new_msg_list

    def delete_checked_messages(self):
        new_msg_list = []
        for msg in self.message_box:
            if msg["trailing1_checked"] == False:
                new_msg_list.append(msg)
        self.message_box = new_msg_list

    def get_all_messages(self):
        return self.message_box

    def get_unchecked_messages_within_timestamp(self, time_from, time_until):
        result = []
        for cmd in self.pending_commands:
            if cmd["timestamp"] >= time_from and cmd["timestamp"] < time_until:
                cmd["ts1checked"] = True
                result.append(cmd)

        return sorted(result, key=itemgetter("timestamp", "eventstamp"))

    def get_all_unchecked_messages_for_rollback_from_timestamp(self, time_from):
        # result_list = []

        # for msg in self.message_box:
        #     if not msg["trailing1_checked"]:
        #         result_list.append(msg)
        #         msg["trailing1_checked"] = True
        result = []
        for cmd in self.pending_commands:
            if cmd["timestamp"] >= time_from:
                result.append(cmd)

        return sorted(result, key=itemgetter("timestamp", "eventstamp"))

    def delete_trailingstate1_checked_messages(self):
        # result_list = []

        # for msg in self.message_box:
        #     if not msg["trailing1_checked"]:
        #         result_list.append(msg)
        #         msg["trailing1_checked"] = True

        newlist = []
        for cmd in self.pending_commands:
            if not cmd["ts1checked"]:
                newlist.append(cmd)

        self.pending_commands = newlist

    def put_message(self, cmd):
        self.msg_counter += 1
        cmd["ts1checked"] = False
        self.pending_commands.append(cmd)
