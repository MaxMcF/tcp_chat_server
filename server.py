from client import ChatClient
import threading
import socket
import sys
import random


PORT = random.randint(1000, 5000)



class ChatServer(threading.Thread):
    def __init__(self, port, host='localhost'):
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
        print('{} connected with {}:{}'.format(client.nick, client.addr[0], str(client.addr[1])))

        try:

            while True:
                data = client.conn.recv(4096)
                self.parser(client, data)
                # if len(data) < 4096:
                #     break

        except (ConnectionResetError, BrokenPipeError, OSError):
            client.conn.close()

        # self.parser(client.id, client.nick, client.conn, message)
        # for cl in self.client_pool:
        #     cl.conn.sendall(message.encode())




    def parser(self, client, message):
        if message.decode().startswith('@'):
            data = message.decode().split(maxsplit=1)
            if data[0] == '@quit':
                client.conn.sendall(b'You have left the chatroom\n')
                reply = client.nick.encode() + b' has left the channel\n'
                [c.client.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.client.id != client.id]
                client.conn.close()
            elif data[0] == '@list':
                user_list = []
                for c in self.client_pool:
                    user_list.append(str(c.nick))
                client.conn.sendall(str(user_list).encode() + b'\n')
            elif data[0] == '@nickname':
                new_nick = data[1].replace('\n', '')
                for c in self.client_pool:
                    if client.id == c.id:
                        c.nick = new_nick
            elif data[0] == '@dm':
                user_and_message = data[1].split(maxsplit=1)
                for c in self.client_pool:
                    if user_and_message[0] == c.nick:
                        message = client.nick.encode() + b': ' + user_and_message[1].encode()
                        c.conn.sendto(message, c.addr)
            else:
                client.conn.sendall(b'Invalid Command, please try again. \n')
        else:
            reply = client.nick.encode() + b': ' + message
            # for cl in self.client_pool:
            #       if len(self.client_pool) > 0:
                    # cl.conn.sendall(reply)
            #     cl.conn.sendall(reply)
            # The line below is the exact same thing
            [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]




    def run(self):
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
