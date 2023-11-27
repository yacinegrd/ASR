import socket
import sys


port, message = int(sys.argv[1]), sys.argv[2]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#client_socket.bind(("localhost", 62000))

client_socket.connect(('localhost', port))

server_message = client_socket.recv(1024)
print(f'server : {server_message.decode()}')

client_socket.send(message.encode())

client_socket.close()