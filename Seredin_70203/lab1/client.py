import socket
import select
import errno
import sys
import time
import datetime
import pytz
import numpy
from tkinter import *
from threading import Thread

HEADER_LENGTH = 32
ENCODING = 'utf-8'
ERROR = 'backslashreplace'

IP = "127.0.0.1"
PORT = 1024

class MyReceivingThread(Thread):
    def __init__(self, clientSocket):
        Thread.__init__(self)
        self.mysocket = clientSocket

    def run(self):
        # write code to receive data from System_1
        while True:
            try:
                while True:
                    time = self.mysocket.recv(HEADER_LENGTH).decode(ENCODING, ERROR).strip()

                    tz = pytz.timezone('Europe/Moscow')
                    time_message = datetime.datetime.fromtimestamp(int(time), tz).strftime('%H:%M')

                    username_header = self.mysocket.recv(HEADER_LENGTH)
                    # print('username_header: {}'.format(username_header))

                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()

                    username_length = int(username_header.decode(ENCODING, ERROR).strip())
                    # print('username_length: {}'.format(username_length))

                    username = self.mysocket.recv(username_length).decode(ENCODING, ERROR)
                    # print('username: {}'.format(username))

                    message_header = self.mysocket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode(ENCODING, ERROR).strip())
                    message = self.mysocket.recv(message_length).decode(ENCODING, ERROR)

                    chat_listbox.insert(END, f'[{time_message}] {username} > {message}')

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
                continue

            except Exception as e:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

def send():
    my_format = u'%H:%M'
    #time = datetime.now().strftime(my_format)
    message = e.get()
    e.delete(0, END)
    if message:

        message = message.encode(ENCODING, ERROR)
        len_message = numpy.uint32(len(message))
        message_header = f"{len_message:<{HEADER_LENGTH}}".encode(ENCODING, ERROR)
        client_socket.send(message_header + message)

def client_to_server():
    message_button = Button(root, text='Send', command=send)
    message_button.pack()

def send_username():
    my_username = e.get()
    e.delete(0, END)
    if my_username:
        username_button.destroy()
        username = my_username.encode(ENCODING, ERROR)
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode(ENCODING, ERROR)
        client_socket.send(username_header + username)
        client_to_server()

root = Tk()
root.title('Client window')
root.geometry('400x250')

chat_frame = Frame(root)
chat_scrollbar = Scrollbar(chat_frame, orient=VERTICAL)

chat_listbox = Listbox(chat_frame, width=50, yscrollcommand=chat_scrollbar.set)

chat_scrollbar.config(command=chat_listbox.yview)
chat_scrollbar.pack(side=RIGHT, fill=Y)
chat_frame.pack()
chat_listbox.pack(pady=15)

e = Entry(root, width=50)
e.pack()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False
while not connected:
    try:
        client_socket.connect((IP, PORT))
        connected = True
    except Exception as e:
        pass #Try again
#client_socket.setblocking(False)

myReceiveThread = MyReceivingThread(client_socket)
myReceiveThread.start()

username_button = Button(root, text='Username', command=send_username)
username_button.pack()
root.mainloop()
