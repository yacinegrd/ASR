import socket
import threading



class Thrd(threading.Thread):
    def __init__(self,client,adr):
        threading.Thread.__init__(self)
        self.client = client
        self.adr = adr
        
    def run(self):
        print(f"device {self.adr} is connected")
        while True :
            msg = self.client.recv(1024)
            print(f"{self.adr} sent : {msg.decode()}")
            if msg.decode() == "bara":
                self.client.close() 
                break

SERVER = socket.gethostname()
PORT = 5050
ADR = (SERVER,PORT)

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind(ADR)
server.listen(5)
print("server started...")

while True :
    client_conn,addr = server.accept()
    cl_thread = Thrd(client_conn,addr)
    cl_thread.start()





