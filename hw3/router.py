import socket
import time
import json
import sys

class Router:
	def __init__(self, routerID, port, file, table):
		## Initializing class variables
		self.port = int(port)
		self.file = file
		self.id = routerID
		## Python Dictionary
		self.table = {}
		self.routes = {}
		self.path = {}

		## Deletes entry for router in routing table
		self.routingTable = table
		del self.routingTable[self.id]

		## Binds to unique port assigned
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(('127.0.0.1', self.port))
		self.sock.settimeout(3)

	def readFile(self):
		## Reads file passed 
		file = open(self.file, "r")
		newTable = {}
		newTable[self.id] = 0.0
		## Creates table from contents in file
		for line in file:
			line = line.split()
			if len(line) == 1:
				continue
			newTable[line[0]] = line[1]

		# Nodes with no direct neighbor will need to find distance to that neighbor
		for node in list(map(chr, range(97,103))):
			if node not in newTable:
				newTable[node] = 16.0

		## Sets table equal to new table
		self.table = newTable

	## Converts table to binary to send over UDP
	def tableToBinary(self):
		string = json.dumps(self.table)
		binary = ' '.join(format(ord(letter), 'b') for letter in string)
		binary = binary.encode()
		return binary

	## Converts recieved binary back to table 
	def binaryToTable(self, binary):
		binary = binary.decode()
		jsn = ''.join(chr(int(x,2)) for x in binary.split())
		dictionary = json.loads(jsn)
		return dictionary

	def shortestPath(self, imported, routerID):
		self.routes = self.table

		## Using empty dictionary generate shortest path table
		for node in list(map(chr, range(97,103))):
			if node == routerID:
				continue
			
			if node in imported and imported[node] != 16.0:
				if float(self.routes[node]) > (float(imported[node]) + float(self.routes[routerID])):
					self.routes[node] = float(imported[node]) + float(self.routes[routerID])

			if node in imported and float(self.routes[node]) == 16.0:
				# Adds distance from router + node distance
				self.routes[node] = float(imported[node]) + float(self.routes[routerID])
	
	## Finds the smallest cost	
	def cost(self):
		self.broadcast()
		try:
			key, addr = self.sock.recvfrom(512)
			if not key.decode == '1':
				dictionary = self.binaryToTable(key)
		except socket.timeout as e:
			print(self.id, "Nothing recieved")

		# Gets ID of the router that we just recieved the table from
		routerID = [key for key in self.routingTable if self.routingTable[key] == addr[1]][0]
		## Implement check for shortest path
		self.shortestPath(dictionary, routerID)

		
	def broadcast(self):
		## Broadcast to neighbor nodes
		for node in self.table:
			if node is self.id:
				continue
			server = ('127.0.0.1', self.routingTable[node])
			table = self.tableToBinary()
			self.sock.sendto(table, server)

	def run(self):
		update = 0
		while 1:
			try:
				self.path = {}
				self.readFile()
				start = time.time()
				received = 0
				# Timed loop instead of timeout
				while time.time() - start < 15 and received < 5:
					self.cost()
					received += 1
				for node in self.routes:
					print(self.id, "->", node, "with cost", self.table[node])

				update += 1
				time.sleep(15)	# Timeout
			except KeyboardInterrupt:
				break