#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Header
"""
import ctypes
from collections import OrderedDict

class Header:
	"""
	Header class handles creating RxP Packet Overheads, 
		manipulating bits of header, and the conversion of header fields 
		to binary and vice versa.
	"""
	_uint8 = ctypes.c_uint8
	_uint16 = ctypes.c_uint16
	_uint32 = ctypes.c_uint32

	def __init__(self, **kwargs):
		# flag fields {FieldName: (Type, NumBytes)}
		self.fields = OrderedDict()
		self._fieldsizes = OrderedDict([
			("srcPort", (self._uint16, 2)),
			("destPort", (self._uint16, 2)),
			("seqNum", (self._uint32, 4)),
			("ackNum", (self._uint32, 4)),
			("flags", (self._uint8, 1)),
			("length", (self._uint16, 2)),
			("recvWindow", (self._uint16, 2)),
			("checksum", (self._uint16, 2))
		])

		fieldKeys = kwargs.keys()
		self.headerLength = 0
		for fieldName, typesize in self._fieldsizes.iteritems():
			fieldType, fieldLength = typesize
			self.headerLength += fieldLength
			if fieldName in fieldKeys:
				fieldValue = kwargs[fieldName]
			else:
				fieldValue = 0	
			self.fields[fieldName] = fieldValue

	def toBinary(self):
		""" Converts the Header Fields to a Binary String """
		headerBytes = bytearray()
		for field in self._fieldsizes.iteritems():
			fieldName, fieldTypeLength = field
			fieldType, numBytes = fieldTypeLength
			fieldValue = self.fields[fieldName]
			if fieldValue is not None:
				headerBytes.extend(bytearray(fieldType(fieldValue)))
		return headerBytes

	@staticmethod
	def unBinary(headerBytes):
		""" Converts the Binary String to Header Fields """
		if not isinstance(headerBytes, bytearray):
			headerBytes = bytearray(headerBytes)
		header = Header()
		base = 0
		for field in header._fieldsizes.iteritems():
			fieldName, fieldTypeLength = field
			fieldType, fieldLength = fieldTypeLength
			fieldValueInBinary = headerBytes[base : base + fieldLength]
			fieldValue = fieldType.from_buffer(fieldValueInBinary).value
			base += fieldLength
			header.fields[fieldName] = fieldValue
		return header

class Flags:
	"""
	Flags class handles conversion of Flag fields to binary and vice versa.
	"""
	_flagTypes = ["SYN", "ACK", "NACK", "FIN", "NM", "EM"]

	@staticmethod
	def toBinary(Flag=None):
		""" Converts list of flags to a binary string """
		if Flag is None:
			inputFlags = ()
		else: inputFlags = list(Flag)
		
		flagsList = []
		for i in range(0, len(Flags()._flagTypes)):
			flagType = Flags()._flagTypes[i]
			if flagType in inputFlags:
				flagsList.append(0b1 << i)
		
		if len(inputFlags) > 0:
			if len(flagsList) > 1:
				byteString = reduce(lambda x, y: x | y, flagsList)
			else: byteString = flagsList[0]
		else: byteString = 0
		return byteString

	@staticmethod
	def unBinary(flagBytes):
		""" Converts binary string to list of flags """
		flags = list()
		for i in range(0, len(Flags()._flagTypes)):
			flagType = Flags()._flagTypes[i]
			if flagBytes >> i & 1:
				flags.append(flagType)
		return tuple(flags)
