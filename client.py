import random
import uuid

class ChatClient:
    def __init__(self, conn=None, addr=None):
        self.id = str(uuid.uuid4())
        self.nick = 'user_{}'.format(random.random())
        self.conn = conn
        self.addr = addr

    def change_name(self, new_name):
        self.nick = new_name

