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

from math import ceil

DATA_CHUNK_SIZE = 500

def DieWithUserMessage(msg, detail):
	""" Die with user message """
	print '\n' + msg + ': ' + detail + '\n'
	sys.exit()


def SendData(sock, dataToSend):
	""" Send data using socket """
	if dataToSend:
		bytesSent = sock.send(dataToSend)
		# if (bytesSent < 0):
		# 	DieWithUserMessage("send()", "failed");
		# elif (sys.getsizeof(dataToSend) != bytesSent):
		# 	# check if bytes sent is the same with size of given data
		# 	DieWithUserMessage("send()", "sent unexpected number of bytes")
		return 0
	else:
		print "SendData(): nothing to send"
		return 1

def ReceiveData(sock):
	""" Receive data using socket """
	bytesReceived, data = sock.recv()
	if (bytesReceived < 0):
		DieWithUserMessage("recv()", "failed");
	elif bytesReceived == 0:
		return 1, None
	return 0, data


def clearCurrentReadline():
	# http://stackoverflow.com/questions/2082387/reading-input-from-raw-input-without-having-the-prompt-overwritten-by-other-th
	# Next line said to be reasonably portable for various Unixes
	(rows,cols) = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ,'1234'))

	text_len = len(readline.get_line_buffer())+2

	# ANSI escape sequences (All VT100 except ESC[0G)
	sys.stdout.write('\x1b[2K')						 # Clear current line
	sys.stdout.write('\x1b[1A\x1b[2K'*(text_len/cols))  # Move cursor up and clear line
	sys.stdout.write('\x1b[0G')						 # Move to start of line


def HandleFxACleint(sock):
	""" 
		Handle FxA Client

		1. Receive Request (GET or POST)
		2. If GET is requested, send requested file. In case of POST,
		   be ready to received specified amount of data chunks

	"""
	# first recieved data would be number of data chunks to receive
	# receive as string and convert to integer
	recvFlag, recvData = ReceiveData(sock)
	if (recvFlag == 1):
		DieWithUserMessage("ReceiveData()", \
			"nothing received even though there's something to receive")
	elif (recvFlag != 0):
		DieWithUserMessage("ReceiveData()", \
			"unknown error")
	request = str(recvData)
	command = request.split(':')
	if (len(command) != 2):
		DieWithUserMessage("HandleFxACleint()", "invalid request")
	elif (command[0].lower() == "get"):
		# When client request is GET request
		fileToSend = command[1]
		if os.path.isfile(fileToSend):
			print "Such file doesn't exist"
		else:
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
						DieWithUserMessage("HandleFxACleint() for GET request", \
							"Expected number of data chunks is different with actual data")
				f.close()
	elif (command[0].lower() == "post"):
		# When client request is POST request
		fileToGet = command[1]

		# first recieved data would be number of data chunks to receive
		# receive as string and convert to integer
		recvFlag, recvData = ReceiveData(sock)
		if (recvFlag == 1):
			DieWithUserMessage("ReceiveData()", \
				"nothing received even though there's something to receive")
		elif (recvFlag != 0):
			DieWithUserMessage("ReceiveData()", \
				"unknown error")
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
	else:
		DieWithUserMessage("HandleFxACleint()", "unknown request")

	""" Clear terminal line and print user command again """ 
	clearCurrentReadline()
	print "Handling Client Like this"
	last_line = readline.get_line_buffer()
	if last_line.endswith('\n'):
		sys.stdout.write('server command > ')
	else:
		sys.stdout.write('server command > ' + readline.get_line_buffer())
	sys.stdout.flush()