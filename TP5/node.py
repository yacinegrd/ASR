import socket as sc
import sys, os, time
from pynput import keyboard
import threading
# le premier neod cree est le consomateur 
# le consomateur consome un message chaque 5s 

class Node:
    def __init__(self, host: str, port: int) -> None:
        # init socket variables
        self.host = host
        self.port = port
        self.sock = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
        
        # bind socket to given addr
        try : self.sock.bind((host, port))
        except OSError: 
            print(f"can't reserve {host}:{port} for this node")
            self.sock.close()
            exit(0) 
        
        self._token = False
        self.next_node = 0
        self.neighbors = Node.get_neighbors()
        self.add_to_bdd()
        self.node_closed = False

    def broadcast(self, msg: str) -> None: # send message to all nodes
        for neighbor_port in self.neighbors:
            self.sock.sendto(msg.encode(), (self.host, neighbor_port))
    
    def add_to_bdd(self) -> None: # add port number to database
        with open('BDD.txt', 'a', encoding='utf-8') as file:
            file.write(f'{self.port}\n')

    def close_node(self) -> None: # properly closing node 
        self.broadcast('QUIT')
        
        self.sock.close()

        with open('BDD.txt', 'r', encoding='utf-8') as file:
            lines = [ line.strip('\n') for line in file.readlines() ]

        with open('BDD.txt', 'w', encoding='utf-8') as file:
            for port in lines: 
                if port != str(self.port): # ignore self port 
                    file.write(f'{port}\n')
        
        self.node_closed = True

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

# envoie message quand il recoi token 
class Producteur(Node):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self.port_consomateur = Producteur.get_consomateur()
        self._send_event = threading.Event()
        self.next_node = self.port_consomateur
        self.broadcast('NEW')
        print('Producteur initialiser')

        
    def get_consomateur() -> int :
        with open('BDD.txt', 'r', encoding='utf-8') as file: 
            return Node.convertPortNumber(file.readlines()[0])

    def receive(self):
        print('receive is running')

        while True:
            try: msg , ( _ , port) = self.sock.recvfrom(1024) 
            except OSError: 
                print('rcv FAILED')
                break
            
            match msg.decode():
                case 'NEW':
                    self.neighbors.append(port)
                    if self.next_node == self.port_consomateur:
                        self.next_node = port
                
                case 'QUIT':
                    self.neighbors.remove(port)
                
                case 'TOKEN':
                    self._token = True
                    print('TOKEN RECEIVED')
                    self._send_event.set()
                
                case 'MEMORY FULL':
                    print('MEMORY FULL')
                    self._send_event.set()
                
                case 'ACK' : 
                    print('message has been sent successfully')
                    self._send_event.set()
        print('rcv closed')

    def send(self):
        while True: 
            self._send_event.wait()
            
            if self.node_closed:
                break
            
            try : msg = input('send message : ')
            except KeyboardInterrupt:
                break
            
            if msg in ['NEW', 'QUIT', 'TOKEN', 'MEMORY FULL', 'ACK']:
                print(f'WARNING : {msg} is not allowed ')
            else:
                self.sock.sendto(msg.encode(), (self.host, self.port_consomateur))
                self._send_event.clear()
        print('send closed')
                
    def on_key_press(self, key):
            match key:
                case keyboard.Key.esc: 
                    if self._token:
                        self.sock.sendto('TOKEN'.encode(), (self.host, self.next_node))
                        self.close_node()
                        self._send_event.set()
                        return False

                case keyboard.Key.tab: # send token on espace
                    print(f'{self.next_node} {self._token}') 
                    if self._token:
                        self._token = False
                        self.sock.sendto('TOKEN'.encode(), (self.host, self.next_node))
                        self._send_event.clear()


# recoi des message et les affiches
class Consomateur(Node):
    def __init__(self, host: str, port: int, max_memory: int) -> None:
        super().__init__(host, port)
        self._token = True
        self.tampon : list[str] = []
        self.max_memory = max_memory

        print('Consomateur initialiser')

    def receive(self) -> None:
        print('receive is running')
        while True:
            try: msg , ( _ , port) = self.sock.recvfrom(1024) 
            except OSError: 
                print('receive stoped running')
                self.close_node() 
                break
            
            match msg.decode():
                case 'NEW':
                    self.neighbors.append(port)
                    if self.next_node == 0 : 
                        self.next_node = port
                
                case 'QUIT':
                    self.neighbors.remove(port)
                    if self.next_node == port and len(self.neighbors) > 0: 
                       self.next_node = self.neighbors[0] 
                
                case 'TOKEN':
                    self._token = True
                    print('TOKEN RECEIVED')
                
                case _:
                    if len(self.tampon) >= self.max_memory:
                        self.sock.sendto('MEMORY FULL'.encode(), (self.host, port))
                    else :
                        self.sock.sendto('ACK'.encode(), (self.host, port))
                        self.tampon.append(msg.decode())

    def consume(self) -> None:
        print('consume is running')
        while True:
            time.sleep(2)
            if self.node_closed:
                break
            if len(self.tampon) > 0:
                print(self.tampon[0])
                self.tampon.pop(0)
        print('consume stoped running')

    
    def on_key_press(self, key):
        match key:
            case keyboard.Key.esc: 
                if self._token:
                    print('haha')
                    self.sock.sendto('TOKEN'.encode(), (self.host, self.next_node))
                    self.close_node()
                    return False # return False stops the event listner
            case keyboard.Key.tab: # send token on espace 
                print(f'{self.next_node} {self._token}')
                if self._token:
                    self._token = False
                    self.sock.sendto('TOKEN'.encode(), (self.host, self.next_node))
    

if __name__ == "__main__" :
    
    if os.path.getsize('./BDD.txt') == 0: # check if file is empty 
        node = Consomateur('127.0.0.1', Node.convertPortNumber(sys.argv[1]), 5)

        th_receive = threading.Thread(target=node.receive).start()
        th_consume = threading.Thread(target=node.consume).start()
        with keyboard.Listener(on_release=node.on_key_press) as L:
            L.join()
    
    else :
        node = Producteur('127.0.0.1', Node.convertPortNumber(sys.argv[1]))
        th_receive = threading.Thread(target=node.receive).start()
        th_send = threading.Thread(target=node.send).start()
        with keyboard.Listener(on_release=node.on_key_press) as L:
            L.join()