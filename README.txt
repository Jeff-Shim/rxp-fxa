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
- fxa/fxa_utility.py : FxA Server uses this utility to handle client commands
- fxa/fxa_server.py : Uses rxp_socket to run the FxA server
- fxa/fxa_client.py : Uses rxp_socket to run the FxA client. Handles user input commands.

Instructions for Compiling & Running Application
1. Run NetEmu: "$ python NetEmu.py 5000"
2. Start the server: "$ python fxa/fxa_server.py X A P"
	X: port number at which the FxA-server’s UDP socket should bind to (odd number) 
	A: the IP address of NetEmu
	P: the UDP port number of NetEmu 
3. Start the client: "$ python fxa/fxa_client.py X A P"
	X: the port number at which the FxA-client’s UDP socket should bind to (even number). Should be equal to the server’s port number minus 1. 
	A: the IP address of NetEmu
	P: the UDP port number of NetEmu 

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