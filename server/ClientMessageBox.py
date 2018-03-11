import zmq
import json

class ClientMessageBox(object):
    def __init__(self):
        self.message_box = []
        self.server_id = 1
        self.msg_counter = 1

    def get_list_len(self):
        return len(self.message_box)

    def delete_messages_before(self, time):
        new_msg_list = []
        for msg in self.message_box:
            if msg["timestamp"] >= time:
                new_msg_list.append(msg)
        self.message_box = new_msg_list

    def get_all_messages(self):
        return self.message_box

    def get_messages(self, time_from, time_until):
        result_list = []
        for msg in self.message_box:
            if msg["timestamp"] >= time_from and msg["timestamp"] < time_until:
                result_list.append(msg)

        return result_list

    def put_message(self, input_dict):
        # input sample: {"msg_id" : 1001, "global_id" : 1001, "timestamp": 359}
        input_dict["msg_id"] = self.server_id * 10000 + self.msg_counter
        self.msg_counter += 1
        self.message_box.append(input_dict)

