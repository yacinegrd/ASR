import socket
import threading, os
from datetime import datetime

class Thrd(threading.Thread):
    def __init__(self,client, addr):
        threading.Thread.__init__(self)
        self.client = client
        self.addr = addr
        
    def run(self):
        print(f"device {self.addr} is connected")
        while True :
            msg = self.client.recv(1024).decode()
            print(f"{self.addr} sent : {msg}")
            if msg.lower() == "end" or msg == "":
                print(f"{self.addr} has been disconnected")
                self.client.close() 
                break
            if msg.lower() == "end server":
                print(f"{self.addr} has been disconnected")
                print("server has shutdown")
                self.client.close()
                os._exit(0)

    def get_client_name(self):                    
        return f"{self.addr[0]}:{self.addr[1]}"
                
SERVER = socket.gethostname()
PORT = 5050
ADDR = (SERVER,PORT)
clients = {}

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
    try:
        server.bind(ADDR)
        server.listen()
    except OSError: # bind raise OSError when port is taken
        print("the port number is already taken")
    else:
        print("server started...")
        while True :
            client_conn,addr = server.accept()
            cl_thread = Thrd(client_conn, addr)
            clients[cl_thread.get_client_name()] = {"port": cl_thread.addr, "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S") }
            print(clients)
            cl_thread.start()
