#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Packet
"""
import math
import rxp_header

class Packet:
	def __init__(self, header=None, data=None):
		if header is None:
			self.header = rxp_header.Header()
		else:
			self.header = header
