# Protocals import
from Select import Select_server
from Go import Go_server

import socket
import sys

class Server:
	def __init__(self):
		self.HOST = '127.0.0.1'
		self.PORT = sys.argv[1]
		self.PROTO = sys.argv[2]
		self.buffer = sys.argv[3]

		if self.PROTO == "SR":
			self.PROTOCAL = Select_server(self.PORT, self.buffer)
		else:
			self.PROTOCAL = Go_server(self.PORT, self.buffer)

	# Runs server
	def run(self):
		self.PROTOCAL.run()

	# Clean shutdown
	def clean(self):
		print("[+] Shutting down connecting...\n")
		self.sock.shutdown(1)
		self.sock.close()

# Main function
if __name__ == '__main__':
	server = Server()
	try:
		server.run()

	except KeyboardInterrupt:
		print "Clean close"
		exit()
