import zmq
import json

class MessageBox(object):
    def __init__(self):
        self.message_box = []
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

    def get_messages_within_timestamp(self, time_from, time_until):
        result_list = []
        for msg in self.message_box:
            if msg["timestamp"] > time_from and msg["timestamp"] <= time_until:
                result_list.append(msg)

        return result_list

    def get_unchecked_messages(self):
        result_list = []

        for msg in self.message_box:
            if not msg["trailing1_checked"]:
                result_list.append(msg)
                msg["trailing1_checked"] = True

        return result_list

    def put_message(self, input_dict):
        self.msg_counter += 1
        input_dict["trailing1_checked"] = False
        self.message_box.append(input_dict)
