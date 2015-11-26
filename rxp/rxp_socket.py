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

	_TIMEOUT = 1 # 1 seconds
	_RESEND_LIMIT = 100
	_SEND_WINDOW = 1
	_ACCEPTS_ASCII = False

	def __init__(self):

		# "Your RxP packets will need to be encapsulated in UDP packets."
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.timeout = self._socket.settimeout(self._TIMEOUT)	# SET TIMEOUT
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
		""" Begins the connection handshake process. 
		Sends a SYN signal, receives SYNACK, then sends ACK.
		Connection status is then changed to established.
		"""
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		self.destAddr = destAddress
		self.seqNum.set()
		returnedPacket = self.send("@SYN", sendFlagOnly=True)
		self.ackNum.set(returnedPacket.header.fields["seqNum"] + 1)
		self.send("@ACK", sendFlagOnly=True)
		self.status = ConnectionStatus.ESTABLISHED

	def listen(self):
		""" Makes server socket wait and listen to incoming connection requests """
		# print "socket.listen() called." # DEBUG
		waitingTime = self._RESEND_LIMIT * 100
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		while waitingTime > 0:
			try:
				data, address = self.recvfrom(self.recvWindow)
				packet = self.constructPacket(data, checkSeq=False)
			except socket.timeout:
				waitingTime -= 1
				continue
			except Error as err:
				if err.message == "invalid_checksum":
					print "socket.listen(): invalid checksum. Trying again..."
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
		# print "socket.listen() finished." # DEBUG

	def accept(self):
		""" Accepts incoming connection. Returns sender's address. """
		# print "socket.accept() called." # DEBUG
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		if self.destAddr is None:
			raise Error("No Connection.")
		returnedPacket = self.send("@SYNACK", sendFlagOnly=True)
		self.ackNum.set(returnedPacket.header.fields["seqNum"])
		self.status = ConnectionStatus.ESTABLISHED
		print "Connection established with client: " + str(self.destAddr)

	def sendto(self, packet, address):
		""" Write packet data and send to address """
		self._socket.sendto(packet.toBinary(), address)

	def send(self, message, sendFlagOnly=False):
		""" 
		Write data to stream. 
		Since this make use of UDP's sendto() function,
			this function automatically takes care of destination address
			under connection-established environment.
		Return: return the number of characters sent. 
		"""
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		
		if self.status != ConnectionStatus.ESTABLISHED or sendFlagOnly == True:
			""" Handshake part: when connection is yet established """
			FLAGS = rxp_header.Flags
			if message == "@SYN":
				""" When specified message is SYN """
				flags = FLAGS.toBinary(("SYN",))
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					seqNum = self.seqNum.num,
					flags = flags)
				packet = rxp_packet.Packet(header)
				self.seqNum.nextSeq()
				resendLimit = self._RESEND_LIMIT
				while resendLimit:
					self.sendto(packet, self.destAddr)
					# print "send(@SYN): signal sent from ", self.srcAddr, "to", self.destAddr # DEBUG
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
				if resendLimit <= 0:
					raise Error("connection_timeout")
				return packet
			elif message == "@SYNACK":
				""" When specified message is SYNACK """
				flags = FLAGS.toBinary(("SYN", "ACK"))
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					seqNum = self.seqNum.num,
					ackNum = self.ackNum.num,
					flags = flags)
				packet = rxp_packet.Packet(header)
				self.seqNum.nextSeq()
				resendLimit = self._RESEND_LIMIT
				while resendLimit:
					self.sendto(packet, self.destAddr)
					# print "send(@SYNACK): signal sent from ", self.srcAddr, "to", self.destAddr # DEBUG
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
				if resendLimit <= 0:
					raise Error("connection_timeout")
				return packet
			elif message == "@ACK":
				""" When specified message is ACK """
				flags = FLAGS.toBinary(("ACK",))
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					seqNum = self.seqNum.num,
					ackNum = self.ackNum.num,
					flags = flags)
				packet = rxp_packet.Packet(header)
				self.sendto(packet, self.destAddr)
				# print "send(@ACK): signal sent from ", self.srcAddr, "to", self.destAddr # DEBUG
		else:
			""" 
			When connection is existing, send given data to 
			connected counterpart.
			"""
			dataQ = deque()
			packetQ = deque()
			sentQ = deque()
			prevSeqNum = int(self.seqNum.num)

			headerSize = rxp_header.Header().headerLength
			dataLength = self.recvWindow - headerSize
			for i in range(0, len(message), dataLength):
				""" 
				Split data into chunks and put them into dataQ
				when data is bigger than supported dataLength.
				"""
				if i + dataLength > len(message):
					dataQ.append(message[i:])
					# print "socket.send(): splitted data size is -> " + str(len(message[i:])) # DEBUG
				else: 
					dataQ.append(message[i:i+dataLength])
					# print "socket.send(): splitted data size is -> " + str(len(message[i:i+dataLength])) # DEBUG
			# print "socket.send(): splitted data into " + str(len(dataQ)) + " chunks" # DEBUG

			lastInd = len(dataQ) - 1
			for ind, data in enumerate(dataQ):
				flagsList = list()
				"""
				Add appropriate flags to first of last chunk of data.
				This means if there's only one chunk, it would have both
				NM and EM flags.
				"""
				if ind == 0:
					""" Add NM flag if this data chunk is the first chunk. """
					# print "socket.send(): adding NM flag to first chunk" # DEBUG
					flagsList.append("NM")
				if ind == lastInd:
					""" Add EM flag if this data chunk is the last chunk. """
					# print "socket.send(): adding EM flag to last chunk" # DEBUG
					flagsList.append("EM")
				flags = rxp_header.Flags.toBinary(flagsList)
				header = rxp_header.Header(
					srcPort = self.srcAddr[1],
					destPort = self.destAddr[1],
					seqNum = self.seqNum.num,
					flags = flags)
				packet = rxp_packet.Packet(header, data)
				self.seqNum.nextSeq()
				""" Append created packet to packetQ """
				packetQ.append(packet)

			numResends = self._RESEND_LIMIT
			while packetQ and numResends:
				sendWindow = self._SEND_WINDOW
				while packetQ and sendWindow:
					packet = packetQ.popleft()
					# print "socket.send(): sending data -> " + packet.data[:40] # DEBUG
					self.sendto(packet, self.destAddr)
					prevSeqNum = int(packet.header.fields["seqNum"])
					sendWindow -= 1
					""" 
					Backup sent packets in sentQ for possible 
					not-sent situations.
					"""
					sentQ.append(packet)
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
						# print "socket.send(): received answer is integer." # DEBUG
						while packet < 0:
							packetQ.appendleft(sendQ.pop())
							packet += 1
					elif packet.checkFlags(("SYN","ACK"), exclusive=True):
						# print "socket.send(): received SYN, ACK in send()" # DEBUG
						self.send("@ACK", sendFlagOnly=True)
						numResends = self._RESEND_LIMIT
						sentQ.reverse()
						packetQ.extendleft(sentQ)
						sentQ.clear()
					elif packet.checkFlags(("ACK",), exclusive=True):
						# print "socket.send(): received ACK, confirmed data transfer" # DEBUG
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
					""" 
					The socket is marked non-blocking, and the receive 
					operation would block, or a receive timeout had been set, 
					and the timeout expired before data were received. 
					"""
					continue
				else: raise e
		# print "recvfrom(): received data (shown in raw string): ", str(data) # DEBUG
		return (data, address)

	def recv(self, blocking=False):
		""" 
		Read data from stream. 
		Since this make use of UDP's recvfrom() function,
			this function automatically takes care of source address
			under connection-established environment.
		Return: return the number of characters received. 
		"""
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		waitLimit = self._RESEND_LIMIT
		while waitLimit:
			try:
				if blocking:
					self.timeout = self._socket.settimeout(None)
				data, address = self.recvfrom(self.recvWindow)
				packet = self.constructPacket(data, checkSeq=False)
				if blocking:
					self.timeout = self._socket.settimeout(self._TIMEOUT)
			except socket.timeout:
				print "socket.recv(): timeout. Trying again..." # DEBUG
				waitLimit -= 1
				continue
			except Error as err:
				if err.message == "invalid_checksum":
					print "socket.recv(): invalid checksum value. Trying again..."
					continue
				if err.message == "sequence_mismatch":
					raise err
			else:
				# print "socket.recv(): data received, start processing data" # DEBUG
				if packet.checkFlags(("FIN",)):
					self.send("@ACK", sendFlagOnly=True)
					self._socket.close()
					break
				if packet.header.fields["seqNum"] >= self.ackNum:
					self.ackNum.nextSeq()
					if packet.checkFlags(("NM",), exclusive=False): 
						""" First chunk of message arrived """
						if self._ACCEPTS_ASCII:
							message = ""
						else: 
							message = bytes()

					""" Append received data to message """
					message += packet.data
					self.send("@ACK", sendFlagOnly=True)
					if packet.checkFlags(("EM",), exclusive=False):
						""" Return message if last chunk is received """
						return True, message
				

		""" Return false when wait time exceeds limit """
		return False, "" 

	def close(self):
		""" Closes the connection """
		flags = rxp_header.Flags.toBinary(("FIN"),)
		header = rxp_header.Header(
			srcPort = self.srcAddr[1],
			destPort = self.destAddr[1],
			seqNum = self.seqNum,
			flags = flags)
		packet = rxp_packet.Packet(header)
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
		packet = rxp_packet.Packet.unBinary(data, toString=self._ACCEPTS_ASCII)
		if packet.verifyChecksum() == False:
			raise Error("invalid_checksum")
		if checkSeq: 
			flags = rxp_header.Flags.unBinary(packet.header.fields["flags"])
			isSYN = packet.checkFlags(("SYN",), exclusive=True)
			isACK = packet.checkFlags(("ACK",), exclusive=True)
			packetSeqNum = packet.header.fields["seqNum"]
			socketAckNum = self.ackNum
			if not isSYN and packetSeqNum and socketAckNum != packetSeqNum:
				raise Error("sequence_mismatch")
			elif not isACK:
				self.ackNum.nextSeq()
		if checkAck:
			flags = rxp_header.Flags.unBinary(packet.header.fields["flags"])
			""" 
			Check ACK number is correct. checkAck would be given as 
			sequence number of previous packet. So ACK should be
			ACK == Previous_Sequence_Number + 1 
			"""
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
