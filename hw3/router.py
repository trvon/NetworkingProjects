class Router:
	def __init__(self, routerID, port, file):
		self.port = port
		self.file = file
		self.id = routerID

	
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

	def run(self):
		foo = 2