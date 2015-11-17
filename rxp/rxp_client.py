#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
Reliable Transfer Protocol (RxP)

RxP Client
"""

""" socket()
Creates an endpoint for communication. 
This function wraps UDP’s socket creation and preceding preparations, 
which include getting address information, and running UDP’s socket function.
[e.g. socket(AF_UNSPEC, SOCK_DGRAM, IPPROTO_UDP)]
Return: socket descriptor
"""

""" send(socket_descripter, buffer_to_send, length_of_buffer)
Write data to stream. 
This function should work only when connection is establised. 
	Otherwise, error is returned.
Since this make use of UDP’s sendto() function, 
	this function automatically takes care of destination address 
	under connection-established environment.
Return: return the number of characters sent. -1 is returned on error.
"""

""" recv(socket_descripter, buffer_to_store_data, length_to_receive)
Read data from stream and store it to buffer.
Since this make use of UDP’s recvfrom() function, 
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
	0 when source_address_string’s format doesn’t match with given flag. 
	-1 on error.
"""

""" inet_ntop(flag, network_address, destination_string, destination_string_size)
Converts IPv4 or IPv6 address from binary format(network_address) to 
	string(into destination_string which has destination_string_size available)
Flag is integer flat that indicates whether given network_address is IPv4 or IPv6.
Return pointer to destination_string, NULL on error.
"""

""" connect(socket_descriptor, socket_address, address_length)
Standard connect() could not create connection for UDP, since UDP is connectionless protocol. 
RxP’s connect() will create an object that is similar with TCP’s Transmission Control Block(TCB) 
	which maintain data for each connection. 
	That TCB-like object has socket information, pointers to buffer where data is held, 
	and all other data needed to maintain reliable stream connection.
Return: 0 if connection succeeds, -1 for error.
"""

""" close(socket_descriptor)
Closes connection.
Return: 0 on success, -1 on error.
"""
