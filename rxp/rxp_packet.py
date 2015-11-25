#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Packet
"""
import rxp_header

class Packet:
	"""
	Packet object which includes the RxP header and data.
	"""
	DATASIZE = 3
	def __init__(self, header=None, data=""):
		if header is None:
			self.header = rxp_header.Header()
		else: self.header = header

		if len(data) > DATASIZE:
			self.data = data[0 : DATASIZE-1]
		else: self.data = data

		self.maxWindowSize = 2**16 - self.header.headerLength - 1
		self.header.fields["recvWindow"] = self.maxWindowSize
		self.header.fields["length"] = len(data)
		self.header.fields["checksum"] = self.checksum()

	@staticmethod
	def _add(a, b):
		c = a + b
		return (c & 0xffff) + (c >> 16)

	def checksum(self):
		""" Standard UDP checksum algorithm """
		binaryStr = str(self.toBinary())
		result = 0
		for i in range(0, len(binaryStr) - 1, 2):
			word = ord(binaryStr[i]) + (ord(binaryStr[i+1]) << 8)
			result = self._add(result, word)
		result = ~result & 0xffff
		return result

	def toBinary(self):
		""" Converts Packet header and data into a binary string """
		packetBytes = bytearray().extend(self.header.toBinary())
		if isinstance(self.data, str):
			packetBytes.extend(self.data.encode(encoding='UTF-8'))
		elif isinstance(self.data, bytearray) or isinstance(self.data, bytes):
			packetBytes.extend(self.data)
		return packetBytes

	@staticmethod
	def unBinary(packetBytes, toString=False):
		""" Converts a binary string to Packet header and data """
		headerSize = Header().headerLength
		packet = Packet()
		packet.header = rxp_header.unBinary(packetBytes[0:headerSize])
		if toString:
			packet.data = packetBytes[headerSize:].decode(encoding='UTF-8')
		else: packet.data = packetBytes[headerSize:]
		return packet

	def verifyChecksum(self):
		""" Verifies checksum
		Compares checksum value from header field and a newly calculated checksum
		"""
		packetChecksum = self.header.fields["checksum"]
		return packetChecksum == self.checksum()

	def checkFlags(self, targetFlags, exclusive=False):
		""" Verify expected flags """
		flags = rxp_header.Flags().unBinary(self.header.fields["flags"])
		validFlags = True
		if exclusive and len(flags) != len(targetFlags):
			validFlags = False
		else:
			for flag in targetFlags:
				if flag is not None and flag not in flags:
					validFlags = False
		return validFlags
