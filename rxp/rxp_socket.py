#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Socket
"""
from collections import deque
import random
import socket
import rxp_header
import rxp_packet

class Socket:
	""" socket()
	Creates an endpoint for communication. 
	This function wraps UDP's socket creation and preceding preparations,
	which include getting address information, and running UDP's socket function.
	[e.g. socket(AF_UNSPEC, SOCK_DGRAM, IPPROTO_UDP)]
	"""

	_TIMEOUT = 30
	_RESEND_LIMIT = 100
	_SEND_WINDOW = 1
	_ACCEPTS_ASCII = False

	def __init__(self):

		# "Your RxP packets will need to be encapsulated in UDP packets."
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.timeout = self._socket.settimeout(self._TIMEOUT)	# 30 seconds.
		self.status = ConnectionStatus.NONE	# init to no connection
		self.srcAddr = None
		self.destAddr = None
		self.seqNum = SequenceNumber()
		self.ackNum = SequenceNumber()
		self.recvWindow = rxp_packet.Packet().maxWindowSize

	def bind(self, address=None):
		""" Assigns the address given as address to the socket """
		if address != None:
			self.srcAddr = address
			self._socket.bind(address)
		else:
			raise Error("No address specified.")

	def connect(self, destAddress):
		""" connect(socket_descriptor, socket_address, address_length)
		Standard connect() could not create connection for UDP, 
			since UDP is connectionless protocol. 
			RxP’s connect() will create an object that is similar with 
			TCP’s Transmission Control Block(TCB) which maintain data 
			for each connection. That TCB-like object has socket information, 
			pointers to buffer where data is held, and all other data needed 
			to maintain reliable stream connection.
		Return: 0 if connection succeeds, -1 for error.
		"""
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		self.destAddr = destAddress
		self.seqNum.set()
		returnedPacket = self.send("@SYN")
		self.ackNum.set(returnedPacket.header.fields["seqNum"] + 1)
		self.send("@ACK")
		self.status = ConnectionStatus.ESTABLISHED

	def listen(self):
		""" Makes server socket wait and listen to incoming connection requests """
		waitingTime = self._RESEND_LIMIT * 100
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		while waitingTime > 0:
			try:
				data, address = self.recvfrom(self.recvWindow)
				packet = self._packet(data, checkSeq=False)
			except socket.timeout:
				waitingTime -= 1
				continue
			except Error as err:
				if err.message == "invalid_checksum":
					continue
			else:
				if packet.checkFlags(("SYN",), exclusive=True):
					break
				else: waitLimit -= 1
		if waitingTime == 0:
			raise Error("connection_timeout")
		ack = packet.header.fields["seqNum"] + 1
		self.ackNum.set(ack)
		self.destAddr = address

	def accept(self):
		""" Accepts incoming connection. Returns sender's address. """
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		if self.destAddr is None:
			raise Error("No Connection.")
		self.seqNum.set()
		self.send("@SYNACK")
		self.status = ConnectionStatus.ESTABLISHED

	def sendto(self, packet, address):
		""" Write packet data and send to address """
		self._socket.sendto(packet.toBinary(), address)

	def send(self, message):
		""" 
		Write data to stream. 
		Since this make use of UDP's sendto() function,
			this function automatically takes care of destination address
			under connection-established environment.
		Return: return the number of characters sent. 
		"""
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		
		if self.status != ConnectionStatus.ESTABLISHED:
			FLAGS = rxp_header.Flags
			if message == "@SYN":
				flags = FLAGS.toBinary(("SYN",))
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					seqNum = self.seqNum.num,
					flags = flags)
				packet = Packet(header)
				self.seqNum.nextSeq()
				resendLimit = self._RESEND_LIMIT
				while resendLimit:
					self.sendto(packet, self.destAddr)
					try:
						data, address = self.recvfrom(self.recvWindow)
						packet = self.constructPacket(data=data, address=address, checkSeq=False)
					except socket.timeout:
						resendLimit -= 1
						continue
					except Error as err:
						if (err.message == "invalid_checksum"):
							continue
					else:
						if packet.checkFlags(("SYN", "ACK"), exclusive=True):
							break
				if resendsRemaining <= 0:
					raise Error("connection_timeout")
				return packet
			elif message == "@SYNACK":
				flags = FLAGS.toBinary(("SYN", "ACK"))
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					seqNum = self.seqNum.num,
					ackNum = self.ackNum.num,
					flags = flags)
				packet = Packet(header)
				self.seqNum.nextSeq()
				resendLimit = self._RESEND_LIMIT
				while resendLimit:
					self.sendto(packet, self.destAddr)
					try:
						data, address = self.recvfrom(self.recvWindow)
						packet = self.constructPacket(data=data, address=address, checkSeq=False)
					except socket.timeout:
						resendLimit -= 1
						continue
					except Error as err:
						if err.message == "invalid_checksum":
							continue
						else:
							if packet.checkFlags(("SYN",), exclusive=True):
								resendLimit = self._RESEND_LIMIT
							elif packet.checkFlags(("ACK",), exclusive=True):
								break
			elif message == "@ACK":
				flags = FLAGS.toBinary(("ACK",))
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					ackNum = self.ackNum.num,
					flags = flags)
				self.sendto(Packet(header), self.destAddr)
		else:
			dataQ = deque()
			packetQ = deque()
			sentQ = deque()
			prevSeqNum = self.seqNum.num

			dataLength = rxp_header.Packet.DATASIZE
			for i in range(0, len(message), dataLength):
				if i + dataLength > len(message):
					dataQ.append(message[i:])
				else: dataQ.append(message[i:i+dataLength])

			for data in dataQ:
				flagsList = list()
				if data == dataQ[0]:
					flagsList.append("NM")
				if data == dataQ[-1]:
					flagsList.append("EM")
				flags = rxp_header.Header.toBinary(flagsList)
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					seqNum = self.seqNum.num,
					flags = flags)
				packet = rxp_packet.Packet(header, data)
				self.seqNum.nextSeq()
				packetQ.append(packet)

			numResends = self._RESEND_LIMIT
			while packetQ and numResends:
				sendWindow = self._SEND_WINDOW
				while packetQ and sendWindow:
					packet = packetQ.popleft()
					self.sendto(packet, self.destAddr)
					prevSeqNum = packet.header.fields["seqNum"]
					sendWindow -= 1
					sendQ.append(packet)
				try: 
					data, address = self.recvfrom(self.recvWindow)
					packet = self.constructPacket(data, checkSeq=False, checkAck=prevSeqNum)
				except socket.timeout:
					sendWindow = self._SEND_WINDOW
					numResends -= 1
					sentQ.reverse()
					packetQ.extendleft(sentQ)
					sentQ.clear()
				except Error as err:
					if err.message == "invalid_checksum":
						continue
				else:
					sendWindow += 1
					if isinstance(packet, int):
						while packet < 0:
							packetQ.appendleft(sendQ.pop())
							packet += 1
					elif packet.checkFlags(("SYN","ACK"), exclusive=True):
						self.send("@ACK")
						numResends = self._RESEND_LIMIT
						sentQ.reverse()
						packetQ.extendleft(sentQ)
						sentQ.clear()
					elif packet.checkFlags(("ACK",), exclusive=True):
						self.seqNum.set(packet.header.fields["ackNum"])
						numResends = self._RESEND_LIMIT
						if sentQ:
							sentQ.popleft()

	def recvfrom(self, recvWindow, flags=None):
		while True:
			try:
				data, address = self._socket.recvfrom(self.recvWindow)
				break
			except socket.error as e:
				if e.errno == 35:
					continue
				else: raise e
		return (data, address)

	def recv(self):
		""" 
		Read data from stream. 
		Since this make use of UDP's recvfrom() function,
			this function automatically takes care of source address
			under connection-established environment.
		Return: return the number of characters received. 
		"""
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		if self._ACCEPTS_ASCII:
			message = ""
		else: message = bytes()
		waitLimit = self._RESEND_LIMIT
		while waitLimit:
			try:
				data, address = self.recvfrom(self.recvWindow)
			except socket.timeout:
				waitLimit -= 1
				continue
			try:
				packet = constructPacket(data, checkSeq=False)
			except Error as err:
				if err.message == "invalid_checksum":
					continue
				if err.message == "sequence_mismatch":
					raise err
			else:
				if packet.header.fields["seqNum"] >= self.ackNum:
					self.ackNum.nextSeq()
					message += packet.data
				self.send("@ACK")
				if packet.checkFlags(("FIN",)):
					self.send("@ACK")
					self._socket.close()
					break
		return 0

	def close(self):
		""" Closes the connection """
		flags = rxp_header.Flags.toBinary(("FIN"),)
		header = rxp_header.Header(
			srcPort = self.srcAddr[1],
			destPort = self.destAddr[1],
			seqNum = self.seqNum,
			flags = flags)
		packet = Packet(header)
		self.seqNum.nextSeq()

		waitLimit = self._RESEND_LIMIT
		while waitLimit:
			self.sendto(packet, self.destAddr)
			try:
				data, address = self.recvfrom(self.recvWindow)
				packet = self.constructPacket(data, checkSeq=False)
			except socket.timeout:
				waitLimit -= 1
				continue
			except Error as err:
				if err.message == "invalid_checksum":
					continue
			else:
				if packet.checkFlags(("ACK",), exclusive=True):
					self._socket.close()
					break
				else: waitLimit -= 1

	def constructPacket(self, data, address=None, checkSeq=True, checkAck=False):
		packet = rxp_header.Packet.unBinary(data, toString=self._ACCEPTS_ASCII)
		if packet.verifyChecksum() == False:
			raise Error("invalid_checksum")
		if checkSeq: 
			flags = rxp_header.Flags.unBinary(packet.header.fields["flags"])
			isSYN = packet.checkFlags(("SYN",), exclusive=True)
			isACK = packet.checkFlags(("ACK",), exclusive=True)
			packetSeqNum = packet.header.fields["seqNum"]
			socketAckNum = self.ackNum
			if not isSYN && packetSeqNum && socketAckNum != packetSeqNum:
				raise Error("sequence_mismatch")
			elif not isACK:
				self.ackNum.nextSeq()
		if checkAck:
			flags = rxp_header.Flags.unBinary(packet.header.fields["flags"])
			packetAckNum = packet.header.fields["ackNum"]
			ackCheck = (int(packetAckNum) - checkAck - 1)
			if packetAckNum and ackCheck:
				return ackCheck
		return packet

class SequenceNumber:
	"""
	Handles sequence number generation. 
	When a socket is created, if seq num is not specified, 
		a random num is generated.
	If sequence number exceeds maximum, wrap around to 0.
	Keeps track of seq num and handles returning next num.
	"""
	_MAX_SEQ = 2 ** 16

	def __init__(self, startingSeq=None):
		if startingSeq == None:
			self.num = random.randint(0, self._MAX_SEQ)
		else: self.num = startingSeq

	def set(self, value=None):
		if value == None:
			self.num = random.randint(0, self._MAX_SEQ)
		else: self.num = value

	def nextSeq(self):
		self.num += 1
		if self.num > self._MAX_SEQ:
			self.num = 0
		return self.num

class ConnectionStatus:
	""" Enum to describe the status of socket connection """
	NONE = "none"
	HANDSHAKING = "handshaking"
	ESTABLISHED = "established"

class Error(Exception):
	""" Throws specified exception """
	defaultMessage = "Oops, something went wrong!"
	def __init__(self, errorMessage=None):
		if errorMessage is None:
			self.message = defaultMessage
		else:
			self.message = errorMessage
	def __str__(self):
		return repr(self.message)
