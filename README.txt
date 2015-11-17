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
- rxp/rxp_header.py : Header object for a single packet
- rxp/rxp_packet.py : A single packet object

Instructions for Compiling & Running Application
1. 

Protocol and API Description
 << RxP >>
- rxp_socket.socket() : Creates the RxP socket--an endpoint for communication.
- socket.bind(address) : Binds a socket instance to address and port given by 'address'.

 << FxA >>

Known Bugs or Limitations
- 