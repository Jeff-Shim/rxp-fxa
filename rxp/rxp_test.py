import logging
import subprocess
import os
import sys
import getopt
import ctypes
import threading
import time
from functools import reduce
import rxp_header
import rxp_packet
import rxp_socket

class Test:

	def __init__(self):
		self.tests = list()
		self.clientAddr = None
		self.serverAddr = None
		self.netAddr = None

	def add(self, func, *args):
		self.tests.append((func, args))

	def run(self, test=None, args=(), index=None):

		if test is not None:
			logging.info(test.__name__ + "...")
			success = test(*args)
			logging.info("...done")
			assert success
		elif index is not None:
			self.run(
				test=self.tests[index][0], 
				args=self.tests[index][1])
		else:
			self.runAll()

	def runAll(self):
		for test in self.tests:
			self.run(
				test=test[0], 
				args=test[1])

def testBind(port=8764):
	"""Tests socket.bind()"""
	assertions = []
	s1 = rxp_socket.Socket()
	s2 = rxp_socket.Socket()
	# test binding to a port that should be empty
	try:
		s1.bind(('127.0.0.1', port))
		assertions.append(True)
	except Exception:
		assertions.append(False)

	# test binding to a port that is in use
	try:
		s2.bind(('127.0.0.1', port))
		assertions.append(False)
	except Exception:
		assertions.append(True)

	return all(assertions)

def testFlagsBinary(attrs=None):
	"""tests Flags class"""

	if attrs is None:
		attrs = ('SYN', 'ACK')

	attrsP = rxp_header.Flags.toBinary(attrs)
	attrs2 = rxp_header.Flags.unBinary(attrsP)
 	
	logging.debug(attrs)
	logging.debug(attrs2)

	assert len(attrs) == len(attrs2)

	assertions = []
	for index, item in enumerate(attrs):
		assertions.append(item == attrs2[index])

	return all(assertions)

def testHeaderBinary(fields=None):
	""""tests Header class"""
	HEADER = rxp_header.Header()
	if fields is None:
		attrs = rxp_header.Flags.toBinary(('SYN', 'ACK'))
		fields = {
			"srcPort" : 8080,
			"destPort" : 8081,
			"seqNum" : 12345,
			"ackNum" : 12346,
			"recvWindow" : 4096,
			"length" : 4096,
			"checksum" : 123,
			"attrs" : attrs
			}

	h = rxp_header.Header(**fields)
	h2 = HEADER.unBinary(h.toBinary())

	logging.debug(h)
	logging.debug(h2) 

	assertions = []
	for fieldName in h.fields:
		val1 = h.fields[fieldName]
		val2 = h2.fields[fieldName]
		assertions.append(val1 == val2)

	return all(assertions)

def testPacketBinary(header=None, data="Hello World!"):
	"""tests the Packet class"""

	if header is None:
		attrs = rxp_header.Flags.toBinary(('SYN', 'ACK'))
		header = rxp_header.Header(
			srcPort=8080,
			destPort=8081,
			seq=12345,
			recvWindow=4096,
			attrs=attrs
			)
	
	p1 = rxp_packet.Packet(header, data)
	p2 = rxp_packet.Packet.unBinary(p1.toBinary(), toString=True)

	logging.debug(p1)
	logging.debug(p2)

	assertions = []

	for name in rxp_header.Header().fields:
		f1 = p1.header.fields[name]
		f2 = p2.header.fields[name]
		assertions.append(f1 == f2)

	assertions.append(p1.data == p2.data)

	return all(assertions)

def testPacketChecksum(p=None):
	if p is None:
		attrs = rxp_header.Flags.toBinary(("SYN",))
		header = rxp_header.Header(
			srcPort=8080,
			destPort=8081,
			seq=123,
			recvWindow=4096,
			attrs=attrs)

	p1 = rxp_packet.Packet(header)
	p2 = rxp_packet.Packet.unBinary(p1.toBinary())

	logging.debug("chksum1: " + str(p1.header.fields["checksum"]))
	logging.debug("chksum2: " + str(p2.header.fields["checksum"]))

	print "checksum 1:", str(p1.header.fields["checksum"])
	print "checksum 2:", str(p2.header.fields["checksum"])
	verify = p2.verifyChecksum()
	print verify
	return verify

def testSocketConnect(clientAddr, serverAddr, netAddr, timeout=3):
	def runserver(server):
		try:
			logging.warn("server:LISTENING() called.")
			server.listen()
			logging.warn("server:LISTENING() finished.")
			logging.warn("server:ACCEPT() called.")
			server.accept()
			logging.warn("server:ACCEPT() finished.")
		except Exception as e:
			logging.info("server " + str(e))

	client = rxp_socket.Socket()
	client.bind(clientAddr)
	client.timeout = timeout
	logging.info("Initialized Client")

	server = rxp_socket.Socket()
	server.bind(serverAddr)
	server.timeout = timeout
	logging.info("Initialized Server")

	serverThread = threading.Thread(target=runserver, args=(server,))
	serverThread.setDaemon(True)
	serverThread.start()

	client.connect(netAddr)
	logging.info("client")
	logging.info("ack: " + str(client.ackNum.num))
	logging.info("seq: " + str(client.seqNum.num))

	serverThread.join()
	logging.info("server:")
	logging.info("ack: " + str(server.ackNum.num))
	logging.info("seq: " + str(server.seqNum.num))

	assertions = []

	assertions.append(client.connStatus == ConnectionStatus.ESTABLISHED)
	assertions.append(server.connStatus == ConnectionStatus.ESTABLISHED)
	assertions.append(client.ackNum.num == server.seqNum.num)
	assertions.append(client.seqNum.num == server.ackNum.num)

	return all(assertions)




"""
RUN TEST
"""
C_ADDR = ("127.0.0.1", 8080)
S_ADDR = ("127.0.0.1", 8081)
N_ADDR = ("127.0.0.1", 5000)

opts, args = getopt.getopt(sys.argv[1:], "d")

if opts and "-d" in opts[0]:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)

# set up tests
tester = Test()
tester.add(testBind) # 0
tester.add(testFlagsBinary) # 1
tester.add(testHeaderBinary) # 2
tester.add(testPacketBinary) # 3
tester.add(testPacketChecksum) # 4
tester.add(testSocketConnect, C_ADDR, S_ADDR, N_ADDR, 0.01) # 5

# run tests
tester.run(index=5)
