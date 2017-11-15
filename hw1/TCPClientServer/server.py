#!/usr/bin/python
# Author    Trevon Williams
# Homework 1

import threading
import datetime
import socket
import sys
import os


class Server:

    def __init__(self):
        self.threads = {}
        # Uses running directory for web contents
        self.ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Test if port is passes
        try:
            self.PORT = int(sys.argv[1])
        except IndexError:
            self.PORT = 9999  # Default port when not specified
            print "Default set to 9999\nPlease enter a port with: \"python server.py [port]\"\n"
        self.ADDRESS = ('localhost', self.PORT)
        print "[+] Starting Server..."
        # Server bound to local host and listening
        self.s.bind(self.ADDRESS)
        self.s.listen(1)

    # Spins new thread when new connection established
    def run(self):
        while 1:
            print "[+] Waiting on connection...\n"
            self.connection, self.client_info = self.s.accept()
            try:
                threading.Thread(target=self.getProcess,
                                 args=(self.connection, self.client_info)).start()
            except:
                print "Error: unable to start thread"

    # Recieves requests and sends to commandProcess function
    # For execution of GET or PUT requests
    def getProcess(self, connection, client):
        try:
            data = connection.recv(1024)
            print "Recieved: %s\n" % data.rstrip()
            self.commandProcess(data, connection)

        finally:
            print "[+] Connection to Host closing...\n"
            # self.connection.close()

    # Function uses a switch statement to process GET or PUT request
    def commandProcess(self, request, connection):
        if request[0:3] == 'GET':
            self.get(request, connection)
        else:
            self.put(request, connection)

    # Implementatino of GET request
    def get(self, request, connection):
        # Checks if file can be opened
        file = request.split(' ')[1][1:]
        try:
            self.file = open(file[1:])
        # Request path not in root dir
        except IOError:
            date = datetime.datetime.now().time()
            server = '\nServer: Simple HTTP Server\r\n'
            c = 'Connection: close\r\n\r\n'
            result = 'HTTP/1.1 404 file not found\r\n'
            content = "<!DOCTYPE html><html><body><h1>404 File Not Found</h1></body></html>"
            header = result + str(date) + server + c + content
            connection.send(header)

            print "[+] Shutting down server\n"
            connection.close()
        # File Found
        else:
            date = datetime.datetime.now().time()
            server = '\nServer: Simple HTTP Server\r\n'
            c = 'Connection: close\r\n'
            result = 'HTTP/1.1 200 OK\r\n'
            header = result + str(date) + server + c
            connection.send(header)
            data = self.file.read(1024)
            while(data):
                connection.send(data)
                data = self.file.read(1024)

            print "[+] Shutting down server\n"
            connection.close()

    # Put Request implementation
    def put(self, data, connection):
        date = datetime.datetime.now().time()
        request = data.split(' ')[1][4:]

        file = open(str(request), 'a')

        data = data.split('\n')[3:]
        for line in data:
            file.write(line)

        connection.send('200 OK File Created\r\n\r\n\r\n')
        file.close()
        connection.close()

        # except:
        #    connection.send('File Not Created')
        #    return

    # Shutdown server cleanly
    def shutdown(self):
        print "[+] Shutting down server\n"
        try:
            self.connection.close()
        except AttributeError:
            return

if __name__ == '__main__':
    server = Server()
    try:
        while(1):
            print "[+] Listening"
            server.run()
    except KeyboardInterrupt:
        server.shutdown()
