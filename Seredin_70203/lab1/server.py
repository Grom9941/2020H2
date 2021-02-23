import socket
import select
import signal
import sys
import os
import time

HEADER_LENGTH = 32
ENCODING = 'utf-8'
ERROR = 'backslashreplace'

IP = "127.0.0.1"
PORT = 1024
MAX_CONNECTIONS = 50
EXIT = 0
PID = os.getpid()
print('My PID is:', PID)

def handler(signum, frame):
    print ('Signal handler called with signal', signum)
    try:
        sys.exit(EXIT)
    except SystemExit as e:
        if e.code != EXIT:
            print('Server shuted down')
            raise

    raise IOError("Couldn't open device!")

def receive_message(client_socket, is_time):
    try:
        if is_time:
            time = client_socket.recv(HEADER_LENGTH)

        message_header = client_socket.recv(HEADER_LENGTH)
        # print('message_header: {}'.format(message_header))

        if not len(message_header):
            return False

        message_length = int(message_header.decode(ENCODING, ERROR).strip())
        # print('message_length: {}'.format(message_length))


        data = client_socket.recv(message_length).strip()
        # print('data: {}'.format(data))

        if is_time:
            return { "time": time, "header": message_header, "data": data}
        else:
            return {"header": message_header, "data": data}

    except:
        return False

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen(MAX_CONNECTIONS)

sockets_list = [server_socket]
clients = {}

while True:
    signal.signal(signal.SIGINT, handler)

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket, False)
            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode(ENCODING, ERROR)))

        else:
            message = receive_message(notified_socket, False)

            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode(ENCODING, ERROR)}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            time_now = int(time.time())
            time_message = f"{time_now:<{HEADER_LENGTH}}".encode(ENCODING, ERROR)
            print(f'[{time_message.decode(ENCODING, ERROR).strip()}] Received message from {user["data"].decode(ENCODING, ERROR)}: {message["data"].decode(ENCODING, ERROR)}')
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(time_message + user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]