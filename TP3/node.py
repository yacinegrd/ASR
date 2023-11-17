import socket as sc
import sys

def convertPortNumber(string):
    try :
        port = int(string)
        if not 49152 <= port <= 65535:
            raise ValueError
    except ValueError :
        print("client port number must be an integer between 49152-65535")
        exit(0)
    else:
        return port

def encode_msg(destinataire, message):
    return f'{destinataire}:{message}'.encode()

def decode_msg(msg):
    msg = msg.decode()

    if msg == 'TOKEN':
        return 0, 'TOKEN'

    destinataire , content = msg.split(":")
    destinataire = convertPortNumber(destinataire)

    return destinataire , content 

class Node():
    def __init__(self, host, port, prev_port):
        self.port = port
        self.host = host
        self.node_socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)
        self.node_socket.bind((host, port))

        with open('nodes.txt', 'a', encoding='utf-8') as f:
            f.write(f'{port}-{prev_port}\n')

    def send(self):
        while True:
            print('---------- Menu ----------')
            print('1 - Envoyez un message')
            print('2 - liberer le jeton')
            print('3 - Quiter')

            choix = int(input("Choisir votre option : "))

            if choix == 1:             
                    message = input("Enter your message : ")
                    ports = Node.get_nodes()

                    for i, port in enumerate(ports):
                        print(f'{i} - {port}')
                    
                    dest_choice = int(input('choose your destination :'))
                    if ports[dest_choice] == self.port:
                        print(message)
                        continue

                    self.node_socket.sendto(encode_msg(ports[dest_choice], message), self.get_next_node())    
            
            elif choix == 2:            
                self.node_socket.sendto('TOKEN'.encode(), self.get_next_node())    
                self.receive()
            
            elif choix == 3:
                if not Node.is_last_node():
                    self.node_socket.sendto('TOKEN'.encode(), self.get_next_node())    
                self.close_node()
                break

    def receive(self):
        while True:
            client_message, client_addr = self.node_socket.recvfrom(1024)

            port, msg = decode_msg(client_message)

            if msg == 'TOKEN':
                print('TOKEN recieved')
                self.send()
            if port == self.port:
                print(f'{msg}')
            else:
                self.node_socket.sendto(encode_msg(port ,msg), self.get_next_node())    
    
    def get_nodes():
        ports = []
        with open("nodes.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            port = line.split('-')[0]
            ports.append(convertPortNumber(port))
        return ports
    
    def get_next_node(self):
        with open("nodes.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            port = line.split('-')
            if port[1].strip('\n') == str(self.port):
                return (self.host, convertPortNumber(port[0]))
            
        return -1


    def close_node(self):
        self.node_socket.close()
    
        with open("nodes.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(Node.get_nodes())
       
        with open("nodes.txt", "w", encoding="utf-8") as f:
            for line in lines:
                port = line.split('-')
                if port[0] != str(self.port):
                    f.write(f"{port[0]}-{port[1]}")
        exit(0)

    def is_last_node():
        with open("nodes.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) == 1:
            return True
        else: return False

                    
    
if not 3 <= len(sys.argv) <= 4:
    print("Try using :\n\tpython node.py port_local port_prec token (optional)")
    exit(0)

HOST = sc.gethostname()
PORT_LOCAL = convertPortNumber(sys.argv[1])
PORT_PREC = convertPortNumber(sys.argv[2])
token_held = False

if len(sys.argv) == 4:
    if int(sys.argv[3]) == 1:
        token_held = True

node = Node(HOST, PORT_LOCAL, PORT_PREC)

if token_held:
    node.send()
else:
    node.receive()
