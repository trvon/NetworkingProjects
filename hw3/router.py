import socket
import time
import sys

class Router:
	def __init__(self, routerID, port, file, table):
		self.port = int(port)
		self.file = file
		self.id = routerID
		self.routingTable = table
		del self.routingTable[self.id]
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# self.sock.bind(('127.0.0.0.1', self.port))

	
	def readFile(self):
		file = open(self.file, "r")
		self.table = {}
		for line in file:
			line = line.split()
			if len(line) == 1:
				continue
			self.table[line[0]] = line[1]
		print(self.id, self.table)

	def cost(self):
		bar = 1

	def broadcast(self):
		foo = 1

	def run(self):
		update = 0
		while 1:
			try:
				self.readFile()
				self.cost()
				update += 1
				time.sleep(15)		# 15 second period
			except KeyboardInterrupt:
				break



