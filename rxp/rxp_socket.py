#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Socket
"""
import socket

class Socket:
	""" socket()
	Creates an endpoint for communication. 
	This function wraps UDP's socket creation and preceding preparations,
	which include getting address information, and running UDP's socket function.
	[e.g. socket(AF_UNSPEC, SOCK_DGRAM, IPPROTO_UDP)]
	"""

	def __init__(self):

		# "Your RxP packets will need to be encapsulated in UDP packets."
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.timeout = self._socket.settimeout(30)	# 30 seconds.
		self.status = ConnectionStatus.NONE	# init to no connection
		self.srcAddr = None
		self.destAddr = None

	def bind(self, address):
		""" bind(socket_descripter, socket_address, address_length)
		Assigns the address given as socket_address to the socket referred to by the socket_descriptor.
		address_length indicates size of socket_address structure.
		"""
		self.srcAddr = address

	def accept(self):
		""" accept(socket, socket_address, address_length)
		If connect() is used for client, accept() is used for client. 
		Since both client and server require TCB, 
			accept() also creates corresponding TCB just like connect().
		"""
		if self.srcAddr is None:
			raise Error("Socket is not bound.")
		if self.destAddr is None:
			raise Error("No Connection.")

	""" listen(socket_descripter, number_of_max_pending_connections)
	This function makes server socket to wait and listen to incoming connection request.
	"""

""" send(socket_descripter, buffer_to_send, length_of_buffer)
Write data to stream. 
This function should work only when connection is establised. 
	Otherwise, error is returned.
Since this make use of UDP's sendto() function,
	this function automatically takes care of destination address
	under connection-established environment.
Return: return the number of characters sent. -1 is returned on error.
"""

""" recv(socket_descripter, buffer_to_store_data, length_to_receive)
Read data from stream and store it to buffer.
Since this make use of UDP's recvfrom() function,
	this function automatically takes care of source address
	under connection-established environment.
Return: number of bytes received, -1 on error
"""

""" inet_pton(flag, source_address_string, socket_address_field)
Converts IPv4 or IPv6 address from text(address_string) to 
	binary format(into socket_address_field)
Flag is integer flag that indicates whether given source address string 
	is in format of IPv4 or IPv6.
Return 1 on success,
	0 when source_address_string's format doesn't match with given flag.
	-1 on error.
"""

""" inet_ntop(flag, network_address, destination_string, destination_string_size)
Converts IPv4 or IPv6 address from binary format(network_address) to 
	string(into destination_string which has destination_string_size available)
Flag is integer flat that indicates whether given network_address is IPv4 or IPv6.
Return pointer to destination_string, NULL on error.
"""

class ConnectionStatus:
	""" Enum to describe the status of socket connection """
	NONE = "none"
	HS_SYN_SENT = "handshake - SYN-SENT"
	HS_SYN_RCVD = "handshake - SYN-RCVD"
	HS_ESTABLISHED = "established"

class Error(Exception):
	""" Throws specified exception """
	defaultMessage = "Oops, something went wrong!"
	def __init__(self, errorMessage=None):
		if errorMessage is None:
			self.message = defaultMessage
		else:
			self.message = errorMessage
	def __str__(self):
		return repr(self.message)
