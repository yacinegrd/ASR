import threading as th
import socket as sc
import json, sys 
import os

def show_console_msg(msg : str = ''):
    if not msg == '':
        print(msg)
    print("Press Enter to continue ...")
    input()


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
        self.next_node = 0
        self.node_closed = False
        self.neighbors = Node.get_neighbors()
        
        # add to database
        self.add_to_bdd()

    def broadcast(self, msg: str) -> None : # send message to all nodes
        for neighbor_port in self.neighbors:
            self.sock.sendto(msg.encode(), (self.host, neighbor_port))

    def add_to_bdd(self) -> None : # add port number to database
        with open('database.txt', 'a', encoding='utf-8') as file:
            file.write(f'{self.port}\n')

    def close_node(self) -> None : # closing the node properly
        with open('database.txt', 'r', encoding='utf-8') as file:
            ports = [ line.strip('\n') for line in file.readlines() ] 
        
        with open('database.txt', 'w', encoding='utf-8') as file:
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
        with open('database.txt', 'r', encoding='utf-8') as file:
            return [ Node.convertPortNumber(line) for line in file.readlines() ]

class Producteur(Node):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        
        self.port_consomateur = Producteur.get_consomateur()
        self.next_node = self.port_consomateur

        self.broadcast('NEW')

        th_receive = th.Thread(target=self.recieve)
        th_receive.start()
        self.menu()


    # return the port number int the first line of the file
    def get_consomateur() -> int : 
        with open('database.txt', 'r', encoding='utf-8') as file:
            return Node.convertPortNumber(file.readline())
        
    def menu(self):
        while not self.node_closed:
            os.system('clear' if os.name == 'posix' else 'cls')
            print('       Producteur')

            if self._token:
                print('---------TOKEN---------')
            print("1 - send token")
            print("2 - send message")
            print("3 - refresh")
            print("4 - show info")
            print("5 - quit")

            choix = int(input('Make your choice : '))

            os.system('clear' if os.name == 'posix' else 'cls')
            
            match choix:
                case 1:
                    if self._token:
                        self._token = False
                        self.sock.sendto(b'TOKEN', (self.host, self.next_node))
                    else :
                        show_console_msg("You can't perform this action without the token")
                case 2:
                    if self._token:
                        message = input('Enter your message : ')
                        if message not in ['TOKEN', 'MEMORY FULL', 'NEW', 'QUIT']:
                            self.sock.sendto(message.encode(), (self.host, self.port_consomateur))
                    else:
                        show_console_msg("You can't perform this action without the token")
                case 3: continue    
                case 4:
                    print(f'HOST :      {self.host}')    
                    print(f'PORT :      {self.port}')
                    print(f'NEXT NODE : {self.next_node}')
                    print(f'NEIGHBORS :')
                    for port in self.neighbors:
                        print(f'    {port}')

                    show_console_msg()
                case 5:
                    self.close_node()
                    continue

    
    def recieve(self):
        while not self.node_closed:
            try : 
                message, ( _ , port) = self.sock.recvfrom(1024)
            except OSError : 
                print('quit')
                break

            match message.decode():
                case 'NEW':
                    self.neighbors.append(port)
                    if self.next_node == self.port_consomateur:
                        self.next_node = port
                case 'TOKEN':
                    self._token = True
                case 'MEMORY FULL':
                    continue
                case 'QUIT':
                    self.neighbors.remove(port)



        
class Consomateur(Node):
    def __init__(self, host: str, port: int, max_memory: int) -> None:
        super().__init__(host, port)
        self.messages = []
        self.max_memory = 5
        self._token = True
        
        th_receive = th.Thread(target=self.receive)
        th_receive.start()
        self.menu()

    def menu(self): 
        while not self.node_closed:
            os.system('clear' if os.name == 'posix' else 'cls')
            print('      Consomateur')

            if self._token:
                print('---------TOKEN---------')
            print("1 - send token")
            print("2 - show messages")
            print("3 - consume messages")
            print("4 - refresh")
            print("5 - show info")
            print("6 - quit")

            try:
                choix = int(input('Make your choice : '))
            except ValueError:
                os.system('clear' if os.name == 'posix' else 'cls')
                show_console_msg('Your choice must an integer between 1 and 6 :')
                continue
        
            if choix not in [*range(1,7)]:
                os.system('clear' if os.name == 'posix' else 'cls')
                show_console_msg('Your choice must be between 1 and 6 :')
                continue

            os.system('clear' if os.name == 'posix' else 'cls')


            match choix:
                case 1:
                    if self.next_node == 0:
                        show_console_msg("No producer is runnig for now")
                    elif self._token:
                        self._token = False
                        print(f'sending to ({self.host}, {self.next_node})')
                        print(f'{self.neighbors}')
                        self.sock.sendto(b'TOKEN', (self.host, self.next_node))
                    else :
                        show_console_msg("You can't perform this action without the token")
                case 2:
                    if len(self.messages) == 0:
                        show_console_msg("There's no message to be showen")
                    else:
                        for msg in self.messages:
                            print(f'- {msg}')
                        show_console_msg()
                case 3:
                    if self._token:
                        self.messages.clear()
                    else :
                        show_console_msg("You can't perform this action without the token")
                case 4: continue
                case 5:
                    print(f'HOST :      {self.host}')    
                    print(f'PORT :      {self.port}')
                    print(f'MAX MSG :   {self.max_memory}')
                    print(f'NEXT NODE : {self.next_node}')
                    print(f'NEIGHBORS :')
                    for port in self.neighbors:
                        print(f'    {port}')

                    show_console_msg()
                case 6:
                    self.close_node()
                    continue
                    
    
    def receive(self):
        while not self.node_closed:
            try : 
                message, ( _ , port) = self.sock.recvfrom(1024)
            except (OSError, KeyboardInterrupt) as e : 
                print('quit')
                break

            match message.decode():
                case 'NEW':
                    self.neighbors.append(port)
                    if self.next_node == 0:
                        self.next_node = port
                case 'TOKEN':
                    self._token = True
                case 'QUIT':
                    self.neighbors.remove(port)
                case _ :
                    if len(self.messages) < self.max_memory:
                        self.messages.append(f"{port}: {message.decode()}")
                    else:
                        self.sock.sendto(b'MEMORY FULL', (self.host, port))



if __name__ == '__main__':
    host = 'localhost'
    port = Node.convertPortNumber(sys.argv[1])


    if os.path.getsize('database.txt') == 0:
        Consomateur(host, port, max_memory=5)
    else :
        Producteur(host, port)
            