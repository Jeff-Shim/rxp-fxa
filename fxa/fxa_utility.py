#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
File Transfter Application (FxA)

FxA Utility
	This utility functions work in both FxA server and client.
"""

import sys
# import os.path
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def DieWithUserMessage(msg, detail):
	""" Die with user message """
	print '\n' + msg + ': ' + detail + '\n'
	sys.exit()


def SendData(sock, dataToSend):
	""" Send data using socket """
	if dataToSend:
		bytesSent = sock.send(dataToSend)
		if (bytesSent < 0)
			DieWithUserMessage("send()", "failed");
		elif (sys.getsizeof(dataToSend) != bytesSent):
			# check if bytes sent is the same with size of given data
			DieWithUserMessage("send()", "sent unexpected number of bytes")
		return 0
	else:
		print "SendData(): nothing to send"
		return 1

def ReceiveData(sock):
	""" Receive data using socket """
	bytesReceived, data = sock.recv()
	if (bytesReceived < 0):
		DieWithUserMessage("recv()", "failed");
	elif bytesReceived = 0:
		return 1, None
	return 0, data


def HandleFxACleint(sock):
	""" 
		Handle FxA Client

		1. Receive Request (GET or POST)
		2. If GET is requested, send requested file. In case of POST,
		   be ready to received specified amount of data chunks

	"""