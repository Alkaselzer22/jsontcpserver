# jsontcpserver
Simple and quick TCP server/client integration for sending and receiving JSON messages

### Why? ###
* Because I needed to move from HTTP request to TCP for internal signaling.
* Because I didn't have anything like this on my tool belt...
* Because I finally figured out a way to handle the 20million question: How do I know how much data I need to read from the socket?

### What's included ###
* TCP Server, with a ClientConnection class to handle incoming connections
* 'tcpclass': a way to encapsulate the length of the json data being sent
* TCP Client basic implementation, based on server's ClientConnection

### Notes... ###
* This first code snippet uses on tornado's async tcpserver/tcpclient. I will try to later on include an asyncore version.

### Contact? ###
* Sure! Why not? If you have any suggestions, comments or improvements, fell free to contact me!
