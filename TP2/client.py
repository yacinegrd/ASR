import socket 
import sys

try: 
    CLIENT_PORT = int(sys.argv[1])
    if not 49152 <= CLIENT_PORT <= 65535:
        raise ValueError
except ValueError:
    print("client port number must be an integer between 49152-65535")
    exit(0)

CLIENT_ADR = (socket.gethostname(), CLIENT_PORT)
SERVER_PORT = 5050
SERVER_ADR = (socket.gethostname(), SERVER_PORT)

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    client.bind(CLIENT_ADR)
    client.connect(SERVER_ADR)
except ConnectionRefusedError: # connect raise ConnectionRefusedError when server is off or don't allow connections
    print(f"Can't connect to the server {SERVER_ADR}")
except OSError: # bind raise OSError when port is taken
    print("the port number is already taken")
else:
    while True:
        message = input("enter your msg : ")
        client.send(message.encode())
        if message.lower() == "end" or message.lower() == "end server":
            break
finally:
    client.close()