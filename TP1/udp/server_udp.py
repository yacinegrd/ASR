import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(("localhost", 60000))

while True:
    client_message, client_addr = server_socket.recvfrom(1024)
    
    print(f'{client_message.decode()} from {client_addr}')
    
    if client_message.decode() == 'end':
        break

server_socket.close()