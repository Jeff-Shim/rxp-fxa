#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
File Transfter Application (FxA)

FxA Client
"""

import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import rxp.rxp_socket # Import RxP Protocol
from fxa_utility import *
from math import ceil

DATA_CHUNK_SIZE = 500

# Check number of arguments
if len(sys.argv) != 4:
	DieWithUserMessage('Command-line Error', 'fxa-client X A P\n\n' \
		+ 'X: the port number at which the FxA-client\'s UDP socket' \
		+ ' should bind to (even number). Please remember that this' \
		+ ' port number should be equal to the server\'s port number minus 1.\n' \
		+ 'A: the IP address of NetEmu\n' \
		+ 'P: the UDP port number of NetEmu')

portNumber = eval(sys.argv[1])
netemuHost = eval(sys.argv[2])
netemuPort = eval(sys.argv[3])
destAddress = netemuHost, netemuPort

""" Create socket """
sock = socket()
# if sock < 0:
# 	DieWithUserMessage('socket()', 'failed to create a socket')

""" Bind to specified port """
sock.bind(('', portNumber))

""" Get user command from this point """
connection = False # connection is yet established
while True:
	command = raw_input("Type command and press enter: ")
	command = command.split(None) # split given string with whitespaces

	if (command[0].lower() == "connect"):
		""" Establish connection with server (netEmu) """
		if (len(command) > 1):
			print "Wront command: Try again."
		else:
			sock.connect(destAddress)
			if(sock.status == ConnectionStatus.ESTABLISHED):
				connection = True
			else:
				DieWithUserMessage("connect() failed", "connection failed")
			# if(sock.connect(networkAddr, networkPort) < 0):
			# 	DieWithUserMessage("connect() failed", "connection failed")
			# else:
			# 	connection = True

	elif (command[0].lower() == "get"):
		""" Downloads file F from the server 
			(if F exists in the same directory with the FxA-server program) 
		"""
		if (connection != True):
			print "Establish connection before using this command."
		elif (len(command) > 2):
			print "Wront command: Try again."
		else:
			print "Receiving " + fileToGet + "..."

			fileToGet = command[1]	
			request = "get:" + fileToGet
			sendFlag = SendData(sock, request)
			if (sendFlag != 0):
				DieWithUserMessage("GET request failed", \
					"Program failed to create proper request")

			# first recieved data would be number of data chunks to receive
			# receive as string and convert to integer
			recvFlag, recvData = ReceiveData(sock)
			# if (recvFlag == 1):
			# 	DieWithUserMessage("ReceiveData()", \
			# 		"nothing received even though there's something to receive")
			# elif (recvFlag != 0):
			# 	DieWithUserMessage("ReceiveData()", \
			# 		"unknown error")
			numOfChunks = int(recvData)

			# Write binary data to a file
			with open(fileToGet, 'wb') as f:
				# received designated number of data chunks then write it
				for i in range(numOfChunks):
					recvFlag, recvData = ReceiveData(sock)
					if (recvFlag == 1):
						DieWithUserMessage("ReceiveData()", \
							"nothing received even though there's something to receive")
					elif (recvFlag != 0):
						DieWithUserMessage("ReceiveData()", \
							"unknown error")
					# recvData must be binary data. There's no check for this.
					f.seek(0, 2) # go to eof: relative position 0 from eof(2)
					f.write(recvData)
				f.close()

	elif (command[0].lower() == "post"):
		""" Uploads file F to the server (if F exists in the same directory
			with the FxA-client program). 
		"""
		if (connection != True):
			print "Establish connection before using this command."
		elif (len(command) > 2):
			print "Wront command: Try again."
		fileToSend = command[1]
		if os.path.isfile(fileToSend):
			print "Such file doesn't exist"
		else:
			request = "post:" + fileToSend
			sendFlag = SendData(sock, request)
			if (sendFlag != 0):
				DieWithUserMessage("POST request failed", \
					"Program failed to create proper request")

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
					dataChunk = f.read(DATA_CHUNK_SIZE)
					if dataChunk:
						sendFlag = SendData(sock, dataChunk)
						if (sendFlag != 0):
							DieWithUserMessage("SendData()", \
								"Program failed to send data properly")
					else:
						DieWithUserMessage("POST", \
							"Expected number of data chunks is different with actual data")
				f.close()

	elif (command[0].lower() == "disconnect"):
		""" Terminates gracefully from the FxA-server """
		if (connection != True):
			print "Establish connection before using this command."
		elif (len(command) > 1):
			print "Wront command: Try again."
		sock.close() # close connection with server
		connection = False
