import socket 

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client.connect((socket.gethostname(),5050))

while True:
    message = input("enter your msg : ")
    client.send(bytes(message,"UTF-8"))
    if message =="END":
        break

client.close()