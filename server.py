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


    def run_thread(self, id, nick, conn, addr):
        print('{} connected with {}:{}'.format(nick, addr[0], str(addr[1])))

        try:

            while True:
                data = conn.recv(4096)
                self.parser(id, nick, conn, data)
                # if len(data) < 4096:
                #     break

        except (ConnectionResetError, BrokenPipeError, OSError):
            conn.close()

        # self.parser(client.id, client.nick, client.conn, message)
        # for cl in self.client_pool:
        #     cl.conn.sendall(message.encode())




    def parser(self, id, nick, conn, message):
        if message.decode().startswith('@'):
            data = message.decode().split(maxsplit=1)
            if data[0] == '@quit':
                conn.sendall(b'You have left the chatroom\n')
                reply = nick.encode() + b' has left the channel\n'
                [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.id != id]
                conn.close()
            elif data[0] == '@list':
                user_list = []
                for c in self.client_pool:
                    user_list.append(str(c.nick))
                conn.sendall(str(user_list).encode())
            else:
                conn.sendall(b'Invalid Command, please try again. \n')
        else:
            reply = nick.encode() + b': ' + message
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
                args = (client.id, client.nick, client.conn, client.addr),
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
