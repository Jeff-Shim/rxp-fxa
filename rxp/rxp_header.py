#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Header
"""
import ctypes

class Header:
	_uint8 = ctypes.c_uint8
	_uint16 = ctypes.c_uint16
	_uint32 = ctypes.c_uint32

	def __init__(self):
		self.fields = {
			"srcAddr" : (_uint16, 2),
			"destAddr" : (_uint16, 2),
			"seqNum" : (_uint32, 4),
			"ackNum" : (_uint32, 4),
			"flags" : (_uint8, 1)
			"recvWindow" : (_uint16, 2),
			"checksum" : (_uint16, 2)
		}
		self.length = 0
		for field, typesize in self.fields.iteritems():
			fieldType, fieldLength = typesize
			self.length += fieldLength

class Flags:
	_flagTypes = ["SYN", "ACK", "NACK", "FIN"]

