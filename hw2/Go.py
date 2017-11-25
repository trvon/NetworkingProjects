# Implementation of the Selective Repeat algorithm
import time
import random
import socket
import struct
import sys
import os

class Go_client:
	def __init__(self, filename, buffSize, port):
		self.buffSize = int(buffSize)	#bits
		self.file = filename
		self.rano = 0
		self.seqLen = 4 				#bits
		self.timer = 3					#seconds
		self.term = 0.01 				#seconds
		self.port = int(port)
		self.host = ''

	def run(self):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			fileSize = os.stat(self.file).st_size
			server = (self.host, self.port)
			sock.sendto(self.file, server)
			sock.sendto(str(fileSize), server)
			
			sock.settimeout(30)
			try:
				key,addr = sock.recvfrom(1)
			except socket.timeout as e:
				print "Receiver didn't respond"
				sys.exit()

			print "Receiver Connected..."
			print "Receiver address:", addr[0]
			startTime = time.time()	
			with open(self.file, "rb") as f:
				transferred = 0
				sock.settimeout(self.term)
				data = f.read(self.buffSize)
				manager = SenderWindowManager(self.seqLen, self.timer)
				pack = Packet_client(self.seqLen, self.buffSize)
				while(data or manager.existBuffer()):
					while(data and manager.needMorePacket()):
						packet, size = pack.pack(data)
						sock.sendto(packet, server)
						manager.pushPacket(packet)
						transferred += size
						print transferred, "/", fileSize, \
						round(float(transferred)/fileSize*100, 2), "%"
						data = f.read(self.buffSize)
					try:
						ack, addr = sock.recvfrom(self.seqLen)
						manager.receiveAck(ack)
						manager.moveWindow()				
					except socket.timeout as e:
						pass
					pList = manager.packetToResend()
					while(len(pList) != 0):
						sock.sendto(pList.pop(0), server)
			endTime = time.time()
			print "Completed..."
			print "Time elapsed :", str(endTime - startTime)

		except socket.error as e:
			print e
			sys.exit()

class Packet_client(object):
	def __init__(self, sequenceLen, bufSize):
		self.sequenceLength = sequenceLen
		self.sequenceSize = pow(2, self.sequenceLength)
		self.bufferSize = bufSize
		self.formatStr = "!I" + str(self.sequenceLength) + "s" + str(bufSize) + "ss"
		self.sequenceNumber = 0

	def decimalToBinary(self, decimalNumber):
		if(decimalNumber < 2):
			return str(decimalNumber)
		return self.decimalToBinary(decimalNumber /2) + str(decimalNumber%2)

	def pack(self, buf):
		print "Sending Seq: ", self.sequenceNumber
		size = len(buf)
		sequenceString = self.decimalToBinary(self.sequenceNumber)
		if len(sequenceString) < self.sequenceLength:
			sequenceString = ('0' * (self.sequenceLength-len(sequenceString))) + sequenceString
		checksum = self.makeChecksum(size, sequenceString + buf)
		p = struct.pack(self.formatStr, size, sequenceString, buf, checksum)
		self.sequenceNumber = (self.sequenceNumber +1) % self.sequenceSize
		return p, size

	def makeChecksum(self, size, buf):
		sumtp = 0
		ptr = 0
		while(ptr < len(buf)):
			sumtp += ord(buf[ptr])
			ptr += 1
		checksum = struct.unpack("ssss", struct.pack("!I", sumtp))
		return checksum[3]

class SenderWindowManager(object):
	def __init__(self, sequenceLength, time):
		self.sequenceSize = pow(2, sequenceLength)
		self.windowSize = self.sequenceSize /2
		self.sequenceArray = [False] * self.sequenceSize
		self.packetArray = [ ]
		self.timerArray = [ ]
		self.windowStart = 0
		self.windowEnd = self.windowSize
		self.lastSequence = 0
		self.timer = time

	def needMorePacket(self):
		return self.lastSequence != self.windowEnd

	def pushPacket(self, pack):
		self.packetArray.append(pack)
		self.timerArray.append(time.time())
		self.lastSequence = (self.lastSequence +1) % self.sequenceSize

	def moveWindow(self):
		while(self.sequenceArray[self.windowStart]):
			self.windowStart = (self.windowStart +1) % self.sequenceSize
			self.windowEnd = (self.windowEnd +1) % self.sequenceSize
			self.sequenceArray[self.windowEnd] = False
			self.packetArray.pop(0)
			self.timerArray.pop(0)
		
	def receiveAck(self, ack):
		ackNumber = self.binaryToDecimal(ack)
		print "Ack ", ackNumber
		if (ackNumber == 0):
			self.sequenceArray[ackNumber] = True
		elif self.sequenceArray[ackNumber - 1]:
			self.sequenceArray[ackNumber] = True

	def binaryToDecimal(self, binaryString):
		return int(binaryString, 2)
		
	def packetToResend(self):
		currentTime = time.time()
		result = [ ]
		index = 0
		while(self.sequenceArray[index]):
			index += 1
			
		while( index < len(self.timerArray) ):
			if( self.timer < (currentTime - self.timerArray[index]) ):
				print "WindowNumber", index, " resent"
				result.append(self.packetArray[index])
				self.timerArray[index] = currentTime
			index += 1
		return result

	def existBuffer(self):
		return len(self.packetArray) != 0

class Go_server:
	def __init__(self, port, buffsize):
		self.IP = ''
		self.PORT = int(port)
		self.buffSize = buffsize
		self.seqLen = 4
	
	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((self.IP, self.PORT))

		try:
			self.file, addr = sock.recvfrom(1472)
			self.file = "final-select.txt"
			print "FileName :", self.file
			fileSize, addr = sock.recvfrom(1472)
			print "FileSize :", fileSize
			fileSize = int(fileSize)
			sock.sendto("1", addr)

			print "Transfer Start..."
			startTime = time.time()
			with open(self.file, "a") as f:
				received = 0
				manager = ReceiverWindowManager(self.seqLen)
				pack = Packet_server(self.seqLen, self.buffSize)
				while (received < fileSize):
					packet, addr = sock.recvfrom(pack.size)
					sequence, size, buf, Checksum = pack.unpack(packet)

					if(not Checksum ):
						continue

					# Forces error in code
					x = 0
					flag = False
					for i in manager.sequenceArray:
						if (flag is False):
							x = int(sequence,2)
							break
						else:
							continue

					if (flag is False and x % 7 == 0 ):
						time.sleep(2)
						flag = True

					x = bin(x)[2:].zfill(4)

					ack = manager.receivePacket(x, size, buf)
					sock.sendto(str(ack), addr)

					bufToWrite = manager.moveWindow()
					while(len(bufToWrite) != 0):
						tup = bufToWrite.pop(0)
						f.write(tup[1])
						received += tup[0]
						print received, "/", fileSize,\
						round(float(received)/fileSize*100, 2), "%"
			endTime = time.time()
			print "Completed..."
			print "Time elapsed :", str(endTime - startTime)
		except socket.error as e:
			print e
			sys.exit()

class Packet_server(object):
	def __init__(self, sequenceLen, bufSize):
		self.sequenceLength = int(sequenceLen)
		self.sequenceSize = pow(2, self.sequenceLength)
		self.bufferSize = int(bufSize)
		self.formatStr = "!I" + str(self.sequenceLength) + "s" + str(self.bufferSize) + "ss"
		self.sequenceNumber = 0
		self.size = self.sequenceLength + self.bufferSize + 5
	
	def unpack(self, pack):
		result = struct.unpack(self.formatStr, pack)
		check = self.isValidChecksum(result[1] + result[2], result[3])
		if(random.randrange(0,50) == 1):
			check = False
		return result[1], result[0], result[2], check

	def isValidChecksum(self, buf, checksum):
		sumtp = 0
		ptr = 0
		while(ptr < len(buf)):
			sumtp += ord(buf[ptr])
			ptr += 1
		result = struct.unpack("ssss", struct.pack("!I", sumtp))
		return result[3] == checksum
		
class ReceiverWindowManager(object):
	def __init__(self, sequenceLength):
		self.sequenceSize = pow(2, sequenceLength)
		self.windowSize = self.sequenceSize /2
		self.sequenceArray = [False] * self.sequenceSize
		self.bufferArray = [None] * self.windowSize
		self.sizeArray = [0] * self.windowSize
		self.windowStart = 0
		self.windowEnd = self.windowSize

	def receivePacket(self, sequence, size, buf):
		sequenceNumber = self.binaryToDecimal(sequence)
		print "Receive sequence number", sequenceNumber
		if(self.isValidSequenceNumber(sequenceNumber)):
			index = self.sequenceToWindowIndex(sequenceNumber)
			if(self.sequenceArray[sequenceNumber] is False):
				self.bufferArray[index] = buf
				self.sizeArray[index] = size
				self.sequenceArray[sequenceNumber] = True
		return sequence

	def moveWindow(self):
		result = []
		while(self.sequenceArray[self.windowStart]):
			self.windowStart = (self.windowStart +1) % self.sequenceSize
			self.windowEnd = (self.windowEnd +1) % self.sequenceSize
			self.sequenceArray[self.windowEnd] = False
			result.append( (self.sizeArray.pop(0), self.bufferArray.pop(0)) )
			self.sizeArray.append(0)
			self.bufferArray.append(None)
		return result

	def sequenceToWindowIndex(self, sequenceNumber):
		ptr = self.windowStart
		index = 0
		while(ptr != sequenceNumber):
			ptr = (ptr +1) % self.sequenceSize
			index += 1
		return index

	def binaryToDecimal(self, binaryString):
		return int(binaryString, 2)

	def isValidSequenceNumber(self, sequenceNumber):
		if(self.windowStart < self.windowEnd):
			if(self.windowStart <= sequenceNumber and sequenceNumber < self.windowEnd):
				return True
			return False
		if(self.windowEnd < self.windowStart):
			if(sequenceNumber < self.windowEnd or self.windowStart <= sequenceNumber):
				return True
			return False