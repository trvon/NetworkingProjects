# Author:	Trevon and Gabon Williams
import random
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

		self.table = {}
		self.neighbors = {}
		self.routes = {}
		self.graph = {}

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

		self.neighbors = newTable
		# Nodes with no direct neighbor will need to find distance to that neighbor
		for node in list(map(chr, range(97,103))):
			if node not in newTable:
				newTable[node] = 16.0
		## Sets table equal to new table
		self.table = newTable
		file.close()

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
		## Using empty dictionary generate shortest path table
		for node in list(map(chr, range(97,103))):
			if self.id == node:
				self.routes[node] = [node, self.table[node]]

			elif node in imported and imported[node] != 16.0:
				if float(self.table[node]) > (float(imported[node]) + float(self.table[routerID])):
					self.table[node] = float(imported[node]) + float(self.table[routerID])
					self.routes[node] = [routerID, imported[node]] ## routerID

				elif float(self.table[node]) != 16.0:
					if routerID == node and routerID in self.neighbors:
						self.routes[routerID] = [self.id,  self.table[routerID]] ## self.id
						self.graph[node] = imported
			else:
				self.routes[node] = [self.id, self.neighbors[self.id]]
				self.graph[node] = imported

	# We want to get to node
	def missingRoutes(self):
		print(self.id, self.graph)

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
		for node in self.neighbors:
			if node is self.id:
				continue
			server = ('127.0.0.1', self.routingTable[node])
			table = self.tableToBinary()
			self.sock.sendto(table, server)

	def run(self):
		update = 1
		self.readFile()
		while 1:
			try:
				self.path = {}
				self.graph = {}
				start = time.time()
				received = 0
				# Timed loop instead of timeout
				for i in range(len(self.neighbors)):
					self.cost()
					received += 1

				# self.missingRoutes()
				for node in self.table:
					print(node, "->", self.id, "with cost", self.table[node], "\tNext hop:", self.routes[node][0], "with cost:", self.routes[node][1])

				print("Node", self.id, "Update:", update)

				# implements the challenge
				c = random.randint(0, 20)
				node = random.randint(0, len(self.neighbors))
				node = list(self.table)[node]

				val = random.uniform(1, 6)
				val = round(val, 1)

				if c % 11 == 0:
					print("CHALLENGE", self.id, "changes", node, "to", val)
					for line in fileinput.input(self.file, inplace=True):
						l = line.split()
						print(node)
						if l[0] == node:
							print(line)
							line = line.replace(l[1], val)
							print(line)
						sys.stdout.write(line)

				update += 1
				time.sleep(15)	# Timeout
				
			except KeyboardInterrupt:
				break