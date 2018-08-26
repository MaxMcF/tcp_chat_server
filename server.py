from client import ChatClient
import threading
import socket
import sys
import random


PORT = random.randint(1000, 5000)


class ChatServer(threading.Thread):
    def __init__(self, port, host='localhost'):
        """This initializes the server by setting the port, host, and server attributes of the thread.
        This also creates the user pool, which is the list of all the users that are currently in the chatroom.
        """
        super().__init__(daemon=True)
        self.port = port
        self.host = host
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
        )
        self.client_pool = []
        try:
            self.server.bind((self.host, self.port))
        except socket.error:
            print('Bind failure {}'.format(socket.error))
            sys.exit()
        self.server.listen(10)

    def run_thread(self, client):
        """This function logs when a user enters the classroom, then runs an inifinite loop that waits for
        user data to be received, then displays that data.
            ARGS:
                The client info for the connecting user.
        """
        print('{} connected with {}:{}'.format(client.nick, client.addr[0], str(client.addr[1])))
        try:
            while True:
                data = client.conn.recv(4096)
                self.parser(client, data)
        except (ConnectionResetError, BrokenPipeError, OSError):
            client.conn.close()

    def parser(self, client, message):
        """This is the main message decoder method. It first checks if the message started with a "/", which indicates if its
        a command. It then goes through all the possible message commands, and executes the proper one if present. If the entered
        data is not a valid command, and error is returned to the user. If the message does not start with a "/", the text is sent as
        a global message to the chatroom.
            ARGS:
                1. The sending client information
                2. The sent message from said client
        """
        if message.decode().startswith('/'):
            data = message.decode().split(maxsplit=1)
            if data[0] == '/quit':
                client.conn.sendall(b'You have left the chatroom\n')
                reply = client.nick.encode() + b' has left the channel\n'
                [c.client.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.client.id != client.id]
                client.conn.close()
            elif data[0] == '/list':
                user_list = []
                for c in self.client_pool:
                    user_list.append(str(c.nick))
                client.conn.sendall(str(user_list).encode() + b'\n')
            elif data[0] == '/nickname':
                new_nick = data[1].replace('\n', '')
                for c in self.client_pool:
                    if client.id == c.id:
                        c.nick = new_nick
            elif data[0] == '/dm':
                user_and_message = data[1].split(maxsplit=1)
                for c in self.client_pool:
                    if user_and_message[0] == c.nick:
                        message = b'@' + client.nick.encode() + b': ' + user_and_message[1].encode()
                        c.conn.sendto(message, c.addr)
            else:
                client.conn.sendall(b'Invalid Command, please try again. \n')
        else:
            reply = client.nick.encode() + b': ' + message
            [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]

    def run(self):
        """This method uses an infinite loop to keep the chatroom open if called.
        """
        print('Server is running on {}'.format(self.port))
        while True:
            conn, addr = self.server.accept()
            client = ChatClient(conn, addr)
            self.client_pool.append(client)
            threading.Thread(
                target = self.run_thread,
                args = (client, ),
                daemon = True
            ).start()
        pass

    def exit(self):
        self.server.close()


if __name__ == '__main__':
    server = ChatServer(PORT)
    try:
        server.run()
    except KeyboardInterrupt:
        server.exit()
