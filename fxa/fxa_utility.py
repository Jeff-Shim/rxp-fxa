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
import os.path
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from math import ceil

DATA_CHUNK_SIZE = 128000 # 128 kB

def DieWithUserMessage(msg, detail):
	""" Die with user message """
	print '\n' + msg + ': ' + detail + '\n'
	sys.exit()


def SendData(sock, dataToSend):
	""" Send data using socket """
	if dataToSend:
		# print "SendData(): sending data ->", str(dataToSend)[:40] # DEBUG
		bytesSent = sock.send(dataToSend)
		# print "SendData(): sent data successfully"# DEBUG
		# if (bytesSent < 0):
		# 	DieWithUserMessage("send()", "failed");
		# elif (sys.getsizeof(dataToSend) != bytesSent):
		# 	# check if bytes sent is the same with size of given data
		# 	DieWithUserMessage("send()", "sent unexpected number of bytes")
		return 0
	else:
		print "SendData(): nothing to send"
		return 1

def ReceiveData(sock, blocking=False):
	""" Receive data using socket """
	# print "ReceiveData(): trying to receive data..." # DEBUG
	recvFlag, recvData = sock.recv(blocking=blocking)
	# print "ReceiveData(): received data ->", str(recvData)[:40] # DEBUG
	if recvFlag == True:
		return True, recvData
	# if (bytesReceived < 0):
	# 	DieWithUserMessage("recv()", "failed");
	# elif bytesReceived == 0:
	# 	return 1, None
	return False, ""


def HandleFxAClient(sock):
	""" 
		Handle FxA Client

		1. Receive Request (GET or POST)
		2. If GET is requested, send requested file. In case of POST,
		   be ready to received specified amount of data chunks

	"""

	
	# first recieved data would be number of data chunks to receive
	# receive as string and convert to integer
	recvFlag, recvData = ReceiveData(sock, blocking=True)
	if (recvFlag != True):
		DieWithUserMessage("ReceiveData()", \
			"unknown error")
	request = str(recvData)
	command = request.split(':')
	if (len(command) != 2):
		DieWithUserMessage("HandleFxAClient()", "invalid request")
	elif (command[0].lower() == "get"):
		# When client request is GET request
		fileToSend = command[1]
		if not os.path.isfile(fileToSend):
			print "Such file '" + str(fileToSend) + "' doesn't exist"
		else:
			print "Sending " + fileToSend + "..."
			# Get file size and count number of data to send
			fileSize = os.path.getsize(fileToSend)
			numOfChunks = int(ceil(fileSize / DATA_CHUNK_SIZE))
			# Send number of chunks first
			sendFlag = SendData(sock, str(numOfChunks))
			if (sendFlag != 0):
				DieWithUserMessage("SendData()", \
					"Program failed to send data properly")
			# Split file and send data
			with open(fileToSend, "rb") as f:
				for i in range(numOfChunks):
					# print "reading chunk no." + str(i) # DEBUG
					dataChunk = f.read(DATA_CHUNK_SIZE)
					if dataChunk:
						sendFlag = SendData(sock, dataChunk)
						if (sendFlag != 0):
							DieWithUserMessage("SendData()", \
								"Program failed to send data properly")
					else:
						DieWithUserMessage("HandleFxAClient() for GET request", \
							"Expected number of data chunks is different with actual data")
				f.close()
				print "Sent " + fileToSend + " successfully."
	elif (command[0].lower() == "post"):
		# When client request is POST request
		fileToGet = command[1]

		print "Receiving " + fileToGet + "..."

		# first recieved data would be number of data chunks to receive
		# receive as string and convert to integer
		recvFlag, recvData = ReceiveData(sock)
		if (recvFlag != True):
			DieWithUserMessage("ReceiveData()", \
				"unknown error")
		numOfChunks = int(recvData)

		directory = "server-recieved"
		if not os.path.exists(directory):
			os.makedirs(directory)

		# Write binary data to a file
		with open(directory + '/' + fileToGet, 'wb') as f:
			# received designated number of data chunks then write it
			for i in range(numOfChunks):
				recvFlag, recvData = ReceiveData(sock)
				if (recvFlag != True):
					DieWithUserMessage("ReceiveData()", \
						"unknown error")
				# recvData must be binary data. There's no check for this.
				f.seek(0, 2) # go to eof: relative position 0 from eof(2)
				f.write(recvData)
			f.close()
			print "Received " + fileToGet + " successfully."
	else:
		DieWithUserMessage("HandleFxAClient()", "unknown request")