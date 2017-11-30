import socket
import time
import json
import sys

class Router:
	def __init__(self, routerID, port, file, table):
		self.port = int(port)
		self.file = file
		self.id = routerID
		self.table = {}

		self.routingTable = table
		del self.routingTable[self.id]

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(('127.0.0.1', self.port))
		self.sock.settimeout(3)

	def readFile(self):
		file = open(self.file, "r")
		newTable = {}
		
		for line in file:
			line = line.split()
			if len(line) == 1:
				continue
			newTable[line[0]] = line[1]
		# print(self.id, self.table)

	def tableToBinary(self):
		string = json.dumps(self.table)
		binary = ' '.join(format(ord(letter), 'b') for letter in string)
		binary = binary.encode()
		return binary

	def binaryToTable(self, binary):
		binary = binary.decode()
		jsn = ''.join(chr(int(x,2)) for x in binary.split())
		dictionary = json.loads(jsn)
		return dictionary

	def cost(self):
		self.broadcast()
		try:
			key, addr = self.sock.recvfrom(512)
			if not key.decode == '1':
				dictionary = self.binaryToTable(key)
			print(self.id, dictionary, addr)
		except socket.timeout as e:
			print(self.id, "Nothing recieved")
			# continue

	def broadcast(self):
		for node in self.routingTable:
			server = ('127.0.0.1', self.routingTable[node])
			table = self.tableToBinary()
			self.sock.sendto(table, server)

	def run(self):
		update = 0
		while 1:
			try:
				self.readFile()
				start = time.time()
				received = 0
				# Timed loop instead of timeout
				while time.time() - start < 15 and received < 5:
					self.cost()
					received += 1
				time.sleep(15)	# Timeout
			except KeyboardInterrupt:
				break