import socket as sc
import sys, threading
from datetime import datetime

def convertPortNumber(string: str) -> int:
    try :
        port = int(string)
        if not 49152 <= port <= 65535:
            raise ValueError
    except ValueError :
        print("client port number must be an integer between 49152-65535")
        exit(0)
    else:
        return port

class Node():
    def __init__(self, host, port):
        self.port = port
        self.host = host
        
        self.my_list = self.creat_my_list() # getting all nodes in the network
        self.add_port_list() # adding port to data base
        self.pedding_messages = [] 
        
        self.node_socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
        try: self.node_socket.bind((host, port))
        except OSError: 
            print(f"can't reserve {host}:{port} for this node")
            self.node_socket.close()
            exit(0) 

        self.introduce_self()


    def creat_my_list(self) -> list[int]:
        ports = []

        with open('BDD.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            port = convertPortNumber(line)
            if port != self.port:
                ports.append(port)
        
        return ports
    
    def add_port_list(self) -> None:
        with open('BDD.txt', 'a', encoding='utf-8') as f:
            f.write(f'{self.port}\n')
    
    def broadcast(self, message: str) -> None:
        for port in self.my_list:
            self.node_socket.sendto(message.encode(), (self.host, port))

    def introduce_self(self) -> None:
        self.broadcast('NEW')
        
    def registry_in_list(self, port: int) -> None:
        self.my_list.append(port)

    def close_node(self):
        self.broadcast('QUIT')
        self.node_socket.close()
    
        with open("BDD.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
       
        with open("BDD.txt", "w", encoding="utf-8") as f:
            for line in lines:
                port = line.strip('\n')
                if port != str(self.port):
                    f.write(f"{port}\n")

    def receive(self):
        while True:
            try: msg, addr = self.node_socket.recvfrom(1024)
            except OSError: break
            
            if msg.decode() == 'NEW':
                self.my_list.append(addr[1])
            elif msg.decode() == 'QUIT':
                self.my_list.remove(addr[1])
            else:
                current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                self.pedding_messages.append(f'{current_time}: {addr} : {msg.decode()}')


    def handle_treatment(self) -> None:
        while True:
            print('---------- Menu ----------')
            print('1 - Send message')
            print('2 - Show received messages')
            print('3 - Show neighbors')
            print('4 - Quit')

            choix = int(input("Enter your choice : "))

            if choix == 1:  # envoyer un message
                message = input("Enter your message : ")
                for i, port in enumerate(self.my_list):
                    print(f'{i+1} - {port}')

                dest_choice = int(input('choose your destination :')) - 1
                
                self.node_socket.sendto(message.encode(), (self.host, self.my_list[dest_choice]))

            elif choix == 2: # afficher les messages recu
                for msg in self.pedding_messages:
                    print(msg)
                self.pedding_messages.clear()
            
            elif choix == 3: 
                for port in self.my_list:
                    print(f"- {port}")
            
            elif choix == 4 : # quiter
                self.close_node()
                break
            
            else: 
                print('choice nust be between 1 and 4') 
                break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Try using :\n\tpython node.py port_local")
        exit(0)
    
    node = Node(sc.gethostname(), convertPortNumber(sys.argv[1]))


    th_handle_treatemnt = threading.Thread(target=node.handle_treatment)
    th_receive = threading.Thread(target=node.receive)

    th_receive.start()
    th_handle_treatemnt.start()