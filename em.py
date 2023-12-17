import socket 
import threading 
import pickle
import os 
import sys
import time


class Node():
    def __init__(self) :
        self.port = sys.argv[1] 
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.ip = socket.gethostname()
        self.sock.bind((self.ip,int(self.port)))
        self.my_dir = os.path.dirname(__file__)
        self.add_port()
        self.token = False
        self.my_neighbs = self.get_ports()
        self.introduce_self()
        self.flag = threading.Event()

    def add_port(self):
        with open(os.path.join(self.my_dir,"nodes.txt"),"a") as file:
            file.write(f"{self.port}\n")

    def get_location(self):
        if len(self.my_neighbs) > 1 :
            return self.my_neighbs.index(self.port)
        return -1
    def get_ports(self):
        with open(os.path.join(my_dir,"nodes.txt"),"r") as file:
            ports = file.read().splitlines()
        return ports
    def introduce_self(self):
        print(self.my_neighbs)
        if len(self.my_neighbs)>1:
            for port in self.my_neighbs:
                self.sock.sendto(bytes("[NEW]","Utf-8"),(self.ip,int(port)))
    def removeself(self):
        with open(os.path.join(my_dir,"nodes.txt"),"r") as file:
            ports = file.readlines()
        ports.remove(f"{self.port}\n")
        with open(os.path.join(my_dir,"nodes.txt"),"w") as file:
            file.writelines(ports)
    def freeToken(self):
        
        if not self.token :
            print("You don't have TOkenz\n\n")
        
        else :
            if self.get_location() == -1:
                print("You dont have Productors..")
            else :
                loc = self.get_location()
                if loc == len(self.my_neighbs)-1 :
                    self.sock.sendto(bytes("Token","Utf-8"),(self.ip,int(self.my_neighbs[0])))
                else :
                    self.sock.sendto(bytes("Token","Utf-8"),(self.ip,int(self.my_neighbs[loc+1])))

                self.token = False
                print("You sent your Token successfuly..")



class Consumer(Node):
    def __init__(self):
        super().__init__()
        self.token = True
        self.memory = []
        self.capacity = 4
        listening = threading.Thread(target=self.listen)
        listening.start()
        self.menu()
    
    def menu(self):
        while True :
            os.system("cls")
            print("     Consumer    ")
            print("-------TOken------" if self.token else "-----------------")
            print("1- Consume")
            print("3- Productors")
            print("4- Memory")
            print("5- show Ports")
            print("6- show Neighbor")
            print("7- refresh")
            print("8- Exit")
            print("-------------")
        
            choice = input("Enter choice")
            os.system("cls")
            if choice == "1" :
                if self.token:
                    while(len(self.memory)>0):
                        print("Start Consuming")
                        print(self.memory)
                        self.memory.pop()
                        time.sleep(1)
                        os.system("cls")
                    
                    print("Consuming done ...")
                else:
                    print("You don't have TOken")
                os.system("pause")
            elif choice == "2" :
                self.freeToken()
                os.system("pause")
            elif choice == "3" :
                print(self.my_neighbs[1:])
                os.system("pause")

            elif choice == "4" :
                print("Memory :")
                for m in self.memory:
                    print(m)
                os.system("pause")
            elif choice == "5":
                print(f"The ports are :{self.my_neighbs}")
                print(f"self port is  :{self.my_neighbs[0]}")
                os.system("pause")
            elif choice =="6":
                print("Consumer :",self.my_neighbs[0])
                if self.get_location() != -1:
                    print("Neighbor is :",self.my_neighbs[1])
                else:
                    print("No Productors")
                os.system("pause")
            elif choice =="7" :
                continue
            elif choice =="8" :
                self.sock.sendto(bytes("[EXIT]","utf-8"),(self.ip,int(self.port)))
                self.removeself()
                break
            else :
                print("Invalid choice...")

        
    def listen(self):
        while True:
            
            raw_data , adr = self.sock.recvfrom(2048)

            data = raw_data.decode()
            if data =="Token" :
                self.token = True
            elif data == "[NEW]" and adr[1] != self.port:
                self.my_neighbs.append(adr[1])
            elif data == "[EXIT]":
                break  
            else :
                self.memory.append(data)
            if len(self.memory) > self.capacity :
                self.memory = []
            
            
class Productor(Node):
    def __init__(self) -> None:
        super().__init__()
        listening = threading.Thread(target=self.listen)
        listening.start()
        self.menu()


    def send(self):
        if self.token :
            message = input("Enter your message")
            self.sock.sendto(bytes(message,"utf-8"),(self.ip,int(self.my_neighbs[0])))
        else :
            print("You don't have Token")
        

    def menu(self):
        while True :
            os.system("cls")
            print(f"     Productor{self.get_location()}   ")
            print("-------TOken------" if self.token else "-----------------")
            print("1- send message")
            print("2- Free Token")
            print("3- show ports")
            print("4- show Neighbor")
            print("5- refresh")
            print("6- Exit")
            print("------------------")               

            choice = input("Enter your choice")
            os.system("cls")
            
            if choice == "1":
               
                self.send()
                
                os.system("pause")
            elif choice == "2":
                self.freeToken()
                os.system("pause")
            elif choice == "3":
                print(f"The ports are :{self.my_neighbs}")
                print(f"self port is  :{self.my_neighbs[self.get_location()]}")
                os.system("pause")
            elif choice =="4" :
                print("Consumer :",self.my_neighbs[0])
                if self.get_location() == len(self.my_neighbs)-1:
                    print("Neighbor is :",self.my_neighbs[0])
                else :
                    print("Neighbor is :",self.get_location()+1)
                os.system("pause")
            elif choice =="5" :
                continue
            elif choice =="6" :
                self.sock.sendto(bytes("[EXIT]","utf-8"),(self.ip,int(self.port)))
                self.removeself()
                break
            else :
                print("Invalid choice ...")

    def listen(self):
        while True:
            raw_data , adr = self.sock.recvfrom(2048)
            data = raw_data.decode()
            if data =="Token" :
                self.flag.set()
            elif data == "[EXIT]":
                break
            elif data == "[NEW]" and adr[1] != int(self.port):
                self.my_neighbs.append(adr[1])
                


my_dir = os.path.dirname(__file__)
if "nodes.txt" in os.listdir(my_dir):
    with open(os.path.join(my_dir,"nodes.txt"),"r") as file:
        ports = file.read().splitlines()
    
   

    
    if len(ports) == 0:
        Consumer()
    else :
        Productor()
    

else :

    open(os.path.join(my_dir,"nodes.txt"),"w")
    Consumer()
    














