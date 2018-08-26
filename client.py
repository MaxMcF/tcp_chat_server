import random
import uuid

class ChatClient:
    def __init__(self, conn=None, addr=None):
        """This creates a new user in the chat room. The user is initially given an id of a random uuid, and a nickname of a random
        number. This nickname can be changed using the change_name class method directly below this method.
        """
        self.id = str(uuid.uuid4())
        self.nick = 'user_{}'.format(random.random())
        self.conn = conn
        self.addr = addr

    def change_name(self, new_name):
        """This allows the user to change their nickname.
        """
        self.nick = new_name

