#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Socket
"""
import random
import socket

class Socket:
	""" socket()
	Creates an endpoint for communication. 
	This function wraps UDP's socket creation and preceding preparations,
	which include getting address information, and running UDP's socket function.
	[e.g. socket(AF_UNSPEC, SOCK_DGRAM, IPPROTO_UDP)]
	"""

	_TIMEOUT = 30
	_RESEND_LIMIT = 100

	def __init__(self):

		# "Your RxP packets will need to be encapsulated in UDP packets."
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.timeout = self._socket.settimeout(self._TIMEOUT)	# 30 seconds.
		self.status = ConnectionStatus.NONE	# init to no connection
		self.srcAddr = None
		self.destAddr = None
		self.seqNum = SequenceNumber()
		self.ackNum = SequenceNumber()


	def bind(self, address=None):
		""" Assigns the address given as address to the socket """
		if address != None:
			self.srcAddr = address
			self._socket.bind(address)
		else:
			raise Error("No address specified.")

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
		self.status = ConnectionStatus.HANDSHAKING

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
					seqNum = self.seqNum,
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
					seqNum = self.seqNum,
					ackNum = self.ackNum,
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
					ackNum = self.ackNum,
					flags = flags)
				self.sendto(Packet(header), self.destAddr)
		else:
			"""
			TODO: send logic for regular messages
			"""
		return 0

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
		return 0

	def constructPacket(self, data, address=None, checkSeq=True, checkAck=False):
		packet = rxp_header.Packet.unBinary(data, toString=self.acceptStrings)
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
