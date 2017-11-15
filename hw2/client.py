# Protocals import
from Select import Select_client
from Go import Go_client
import socket
import sys


class Client:
	# Initialization 
	def __init__(self):
		self.FILE = sys.argv[1]
		self.HOST = '127.0.0.1'
		self.PORT = sys.argv[2]

		self.buffer = sys.argv[3]
		self.PROTO = sys.argv[4]
		if self.PROTO == "SR":
			self.PROTOCAL = Select_client(self.FILE, self.buffer, self.PORT)
		else:
			self.PROTOCAL = Go_client(self.FILE, self.buffer, self.PORT)

	# Run 
	def run(self):
		self.PROTOCAL.run()

	# Clean shutdown
	def clean(self):
		print "[+] Shutting down connecting...\n"

# Main function
if __name__ == '__main__':
	client = Client()
	try:
		client.run()

	except KeyboardInterrupt:
		print "Clean close"
		exit()