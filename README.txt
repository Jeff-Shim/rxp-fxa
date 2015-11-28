Sung Kim (skim928@gatech.edu)
Minho Shim (minhoshim@gatech.edu)

CS 3251 B : Computer Network I
Programming Assignment 2 
	Reliable Transfer Protocol (RxP)
	File Transfer Application (FxA)
Due Nov. 25, 2015

===============================================================
	Files Submitted (Names & Description)
- rxp/rxp_socket.py : Contains all logic for creating and manipulating RxP Socket
- rxp/rxp_header.py : Header object for a single packet. Prepended to packet object
- rxp/rxp_packet.py : A single packet object
- fxa/fxa_utility.py : FxA Server uses this utility to handle client commands
- fxa/fxa_server.py : Uses rxp_socket to run the FxA server
- fxa/fxa_client.py : Uses rxp_socket to run the FxA client. Handles user input commands.
- rxp/__init__.py : Supports import of RxP from FxA
- fxa/test.jpg : Image file for test purpose

===============================================================
	Instructions for Compiling & Running Application
1. Run NetEmu: "$ python NetEmu/NetEmu.py 5000"
2. Start the server: "$ python fxa/fxa_server.py X A P"
	X: port number at which the FxA-server’s UDP socket should bind to (odd number) 
	A: the IP address of NetEmu
	P: the UDP port number of NetEmu 
	COMMANDS:
		window W : Set window size at FxA-server
		terminate : shut-down FxA Server
3. Start the client: "$ python fxa/fxa_client.py X A P"
	X: the port number at which the FxA-client’s UDP socket should bind to (even number). Should be equal to the server’s port number minus 1. 
	A: the IP address of NetEmu
	P: the UDP port number of NetEmu 
	COMMANDS:
		connect : FxA client connects with FxA server
		get F : FxA client downloads file F from server
		post F : FxA client uploads file F to server
		window W : Set window size at FxA-client
		disconnect : FxA client closes connection with FxA server (connection must already be established)

===============================================================
	RxP Protocol Description

Pipelining
	RxP is an implementation of Go-Back-N ARQ protocol. 
	The sender will send a specified number of packets (window size) with exact sequence numbers. The receiver will return an ACK for the last correct in-order packet.

Corrupt Packets
	A packet is determined to be corrupt when it fails the standard checksum algorithm. 
	The sender sends a packet with a sequence number, and expects to receive an ACK with the exact acknowledge number. However, if the receiver receives the packet and finds it to be corrupt after running it through checksum, it does not send an ACK, thus forcing the sender to send the packet again.

Lost Packets
	Much like corrupt packets, the sender sends a packet with an exact sequence number. If a correct ACK is not returned by the receiver, then it is assumed that the packet was lost along the way and sender resends the packet.

Out-of-Order Packets
	In this Go-Back-N ARQ implementation, RxP sends a window of packets. The only way this window is considered successful is if a single ACK is returned with the exact acknowledge number, which should be (sequence number of first packet in the window + window size + 1). The only way to produce this exact ACK is if all sequence numbers increment sequentially to properly increment the receiver's acknum.

Bi-Directional Data Transfers
	Bi-directional data transfer is handled by default in RxP implementation. RxP socket is versatile enough to be used in either client or socket, so sending and receiving can be done the same way on either sides. 

===============================================================
	RxP API Description

- rxp_socket.Socket() 
	Creates the RxP socket--an endpoint for communication. Used for both client and server
	ex. "socket = Socket()"

- socket.bind(address) 
	Binds a socket instance to address and port given by 'address'.
	ex. "socket.bind(('127.0.0.1', 8080))"

- socket.listen()
	Socket waits and listens for incoming connection request.
	ex. "socket.listen()"

- socket.connect(address)
	Socket connects to a remote socket at 'address'.
	ex. "socket.connect(('127.0.0.1', 8081))"

- socket.accept()
	Socket accepts incoming connection.
	ex. "socket.accept()"

- socket.send(message, sendFlagOnly)
	Used to either send handshake signals or send datagrams.
	message : message to send. Byte stream or string.
	sendFlagOnly : boolean for whether to send empty packet with signals in header or send packet with data
	ex. "socket.send("@SYN", sendFlagOnly=True)" - sends SYN signal
	ex. "socket.send("Hello World", sendFlagOnly=False)" - sends message to receiver specified in socket.destAddr

- socket.recv(blocking)
	Used to either receive handshake signals or receive datagrams.
	blocking : boolean to halt loop until something is received
	ex. "socket.recv(blocking=False)"

- socket.close()
	Terminates the connection.
	ex. "socket.close()"

===============================================================
	Known Bugs or Limitations
- During RxP handshake, when there are errors, sometimes the ACK doesn't go through. If the ACK is not successfully sent through, the server will continue to repeatedly send SYNACK until either an ACK or a new message comes through.
- At the end of a message, when there are errors, sometimes the final ACK doesn't go through. The server will just continue to listen for the ACK and timeout. This will not cause any errors with the message.
- Performance of error handling decreases with higher percentage of possible errors passed into NetEmu. In other words, if error rates set in NetEmu is too high, limit of resending will be reached and raise error. This is obvious and practical.
- FxA server isn't too 'graceful' in terminating.
