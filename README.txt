Sung Kim (skim928@gatech.edu)
Minho Shim (minhoshim@gatech.edu)

CS 3251 B : Computer Network I
Programming Assignment 2 
	Reliable Transfer Protocol (RxP)
	File Transfer Application (FxA)
Due Nov. 25, 2015

Files Submitted (Names & Description)
- rxp/rxp_socket.py : Contains all logic for creating and manipulating RxP Socket
- rxp/rxp_server.py : Contains all logic for running RxP Server
- rxp/rxp_client.py : Contains all logic for running RxP Client
- rxp/rxp_header.py : Header object for a single packet. Prepended to packet object
- rxp/rxp_packet.py : A single packet object

Instructions for Compiling & Running Application
1. 

Protocol and API Description
 << RxP >>
+ rxp_socket.socket() : Creates the RxP socket--an endpoint for communication.
- socket.bind(address) : Binds a socket instance to address and port given by 'address'.
- socket.listen(): Socket waits and listens for incoming connection request.
- socket.connect(): Socket connects endpoints for communication.
- socket.accept(): Socket accepts incoming connection.
- socket.send(): Used to either send handshake signals or send datagrams.
- socket.recv(): Used to either recv handshake signals or recv datagrams.
- socket.close(): Terminates the connection.

 << FxA >>

Known Bugs or Limitations
- 