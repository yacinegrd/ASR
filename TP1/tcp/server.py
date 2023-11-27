import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(("localhost", 60000))

server_socket.listen()

while True:
    client_socket , client_adresse = server_socket.accept()

    client_socket.send(f'welcome to the server {server_socket.getsockname()}'.encode())
    client_message = client_socket.recv(1024)

    print(f'{client_message.decode()} -- du client {client_socket.getsockname()}')

    client_socket.close()
    if client_message.decode() == 'end':
        break

server_socket.close()

