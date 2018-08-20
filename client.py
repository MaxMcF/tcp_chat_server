import random
import uuid

class ChatClient:
    def __init__(self, conn=None, addr=None):
        self.id = str(uuid.uuid4())
        self.nick = self
