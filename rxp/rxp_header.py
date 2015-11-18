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
	_uint8 = ctypes.c_uint8
	_uint16 = ctypes.c_uint16
	_uint32 = ctypes.c_uint32

	def __init__(self, **kwargs):
		# flag fields {FieldName: (Type, NumBytes)}
		self.fields = OrderedDict()
		self._fieldsizes = OrderedDict([
			("srcAddr", (self._uint16, 2)),
			("destAddr", (self._uint16, 2)),
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
		header = Header()
		base = 0
		
		return header

class Flags:
	_flagTypes = ["SYN", "ACK", "NACK", "FIN"]
