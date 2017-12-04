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
		## https://docs.python.org/3/tutorial/datastructures.html
		self.table = {}
		self.routes = {}

		## Deletes entry for router in routing table
		self.routingTable = table
		del self.routingTable[self.id]

		## Binds to unique port assigned
		## https://docs.python.org/3/library/socket.html
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(('127.0.0.1', self.port))
		self.sock.settimeout(3)

	def readFile(self):
		## Reads file passed 
		## https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
		file = open(self.file, "r")
		newTable = {}
		newTable[self.id] = 0.0
		## Creates table from contents in file
		for line in file:
			line = line.split()
			## We don't really need to know how many connections if the file has 
			## all the connections.
			if len(line) == 1:
				## If you need to see that the line prints the amount of neighbors
				## contained within the router table in the file
				# print(line)
				continue
			newTable[line[0]] = line[1]

		# Nodes with no direct neighbor will need to find distance to that neighbor
		for node in list(map(chr, range(97,103))):
			if node not in newTable:
				newTable[node] = 16

		## Sets table equal to new table
		self.table = newTable
		# self.routes = self.table
		# print(self.id, self.table)

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

	## We need to implement the distance vector protocal to find the shortest path
	## From the recieved tables broadcasted by all routers
	def shortestPath(self, imported):
		## Using empty dictionary generate shortest path table
		for node in list(map(chr, range(97,103))):
			if node in self.routes and node in imported:
				if float(self.routes[node]) > float(imported[node]):
					self.routes[node] = float(imported[node])
			elif node in imported:
				self.routes[node] = float(imported[node])

			# Path not defined
			if self.routes[node] == 16:
				doSomeLogic = True
	
	## Finds the smallest cost	
	def cost(self):
		self.broadcast()
		try:
			key, addr = self.sock.recvfrom(512)
			if not key.decode == '1':
				dictionary = self.binaryToTable(key)

		except socket.timeout as e:
			print(self.id, "Nothing recieved")

		## Implement check for shortest path
		self.shortestPath(dictionary)

		
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
				node = ''
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