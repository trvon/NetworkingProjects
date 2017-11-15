#!/usr/bin/python
# Author    Trevon Williams, Gabon Williams
# Project 1

import urlparse
import socket
import sys


class Client:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        url = urlparse.urlparse(sys.argv[1])
        self.PORT = int(sys.argv[2])
        self.HOST = url.path
        self.COMMAND = sys.argv[3]
        try:
            self.FILENAME = sys.argv[4]
        except IndexError:
            self.FILENAME = None

    def run(self):
        if self.COMMAND == 'GET':
            self.get()
        else:
            self.put()

    # PUT request
    def put(self):
        status = self.httpConnect()
        if status == 1:
            return

        # Checking if value is defined
        if self.FILENAME is not None:
            file = open('./' + self.FILENAME, 'r')
            self.s.send('PUT /?q=%s HTTP/1.1\t\n\t\n' % self.FILENAME)
        else:
            return

        f = file.read()
        self.s.sendall(f)

        response = self.s.recv(1024)
        print response
        file.close()

    # GET request
    def get(self):
        status = self.httpConnect()
        if status == 1:
            return
        # If not page defined goto home page
        if self.FILENAME is None:
            self.s.send('GET /%s HTTP/1.1\r\n\r\n' % 'index.html')
        # Passes file to GET request
        else:
            self.s.send('GET /%s HTTP/1.1\r\n\r\n' % self.FILENAME)
        print "\n[+] Host responded with:\n"

        # Continues to recv data until stream ends
        while(1):
            try:
                response = self.s.recv(2048)
                print response.strip()
                if not response:
                    break
            except socket.timeout:
                # Add code to handle times to host
                print "[+] Timeout\n"
                break
        print "[+] Shutting down connecting...\n"

    # Establishes HTTP Connection
    def httpConnect(self):
        # self.s.settimeout(0.50)
        try:
            self.s.connect((self.HOST, self.PORT))
            print "\n[+] Connected to %s\n" % self.HOST
        except socket.error:
            print "\n[+] Couldn't connect to Host"
            return 1

    # Clean shutdown
    def clean(self):
        print "[+] Shutting down connecting...\n"
        self.s.shutdown(1)
        self.s.close()

# Main function
if __name__ == '__main__':
    client = Client()
    try:
        client.run()

    except KeyboardInterrupt:
        client.clean()
