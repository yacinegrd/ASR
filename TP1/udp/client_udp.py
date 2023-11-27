import socket
import sys


port, message = int(sys.argv[1]), sys.argv[2]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto(message.encode(), ('localhost', port))

client_socket.close()

print(client_socket)