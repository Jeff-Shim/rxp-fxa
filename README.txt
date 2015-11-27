Sung Kim (skim928@gatech.edu)
Minho Shim (minhoshim@gatech.edu)

CS 3251 B : Computer Network I
Programming Assignment 2 
	Reliable Transfer Protocol (RxP)
	File Transfer Application (FxA)
Due Nov. 25, 2015

Files Submitted (Names & Description)
- rxp/rxp_socket.py : Contains all logic for creating and manipulating RxP Socket
- rxp/rxp_header.py : Header object for a single packet. Prepended to packet object
- rxp/rxp_packet.py : A single packet object

Instructions for Compiling & Running Application
1. Run NetEmu: "$ python NetEmu.py 5000"
2. Start the server: "$ python fxa/fxa_server.py 8081 127.0.0.1 5000"
	where 8081 is the source port (must be odd),
	      127.0.0.1 is the source address,
	      5000 is the destination port (same as NetEmu port)
3. Start the client: "$ python fxa/fxa_client.py 8080 127.0.0.1 5000"
	where 8080 is the source port (must be even and -1 from server port)
	      127.0.0.1 is the source address,
	      5000 is the destination port (same as NetEmu port)

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

Known Bugs or Limitations
- 