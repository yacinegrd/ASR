# changes that will be made 
# using non blocking recv and input fuction for stopping the programme 
# let see after that
import socket as sc 
import threading as th
import sys
import json

class Node:
    def __init__(self, host: str, port: int) -> None:
        # init socket variables 
        self.host = host 
        self.port = port 
        self.sock = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)

        # bind socket to given address 
        try : self.sock.bind((host, port))
        except OSError:
            print(f"can't reserve {host}:{port} for this node")
            self.sock.close()
            sys.exit(0)

        # init node variables
        self._token = False
        self.node_closed = False
        self.next_node = 0
        self.neighbors = Node.get_neighbors()
        
        # add to database
        self.add_to_bdd()

    def broadcast(self, msg: str) -> None : # send message to all nodes
        for neighbor_port in self.neighbors:
            self.sock.sendto(msg.encode(), (self.host, neighbor_port))

    def add_to_bdd(self, msg: str) -> None : # add port number to database
        with open('BDD.txt', 'a', encoding='utf-8') as file:
            file.write(f'{self.port}\n')

    def close_node(self) -> None : # closing the node properly
        with open('BDD.txt', 'r', encoding='utf-8') as file:
            ports = [ line.strip('\n') for line in file.readlines() ] 
        
        with open('BDD.txt', 'w', encoding='utf-8') as file:
            for port in ports:
                if port != str(self.port): # ignore self port 
                    file.write(f'{port}\n')

        self.broadcast('QUIT')
        self.node_closed = True
        self.sock.close()
    
    def convertPortNumber(string: str) -> int: # convert port number from str to int
        try :
            port = int(string)
            if not 49152 <= port <= 65535:
                raise ValueError
        except ValueError :
            print("client port number must be an integer between 49152-65535")
            exit(0)
        else: 
            return port
    
    def get_neighbors() -> list[int]:
        with open('BDD.txt', 'r', encoding='utf-8') as file:
            return [ Node.convertPortNumber(line) for line in file.readlines() ]


class Producteur(Node):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self.port_consomateur = Producteur.get_consomateur()
        self.next_node = self.port_consomateur

        self._send_event = th.Event()
        self.broadcast('NEW')

        print('Producteur initialiser')

    # read the first line in the database 
    # and return the port number written in it
    def get_consomateur() -> int : 
        with open('BDD.txt', 'r', encoding='utf-8') as file:
            return Node.convertPortNumber(file.readline())
    
    def receive(self):
        print("receive is running")

        while not self.node_closed:
            try: msg , (_, port) = self.sock.recvfrom(1024)
            except sc.timeout:
                continue
            except sc.error as e: 
                self.close_node()
                print(e)
                sys.exit(0)
            
            match msg.decode():
                case "NEW":
                    self.neighbors.append(port)
                    if self.next_node == self.port_consomateur:
                        self.next_node = port

                case "QUIT":
                    self.neighbors.remove(port)

                case "TOKEN":
                    self._token = True
                    print("TOKEN RECEIVED")
                    self._send_event.set()

                case "MEMORY FULL":
                    print('MEMORY FULL')
                    self._send_event.set()

                case 'ACK':
                    print('message has been sent successfully')
                    self._send_event.set()
            
    def send(self):
        while not self.node_closed:
            pass # non blocking input
