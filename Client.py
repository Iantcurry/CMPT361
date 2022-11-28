import socket
import os
import sys
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def viewEmail(clientSocket):
    message = clientSocket.recv(2048)
    message = message.decode('ascii')
    # decrpyt #
    
    index =  input("Enter the email index you wish to view: ")
    # encrypt #
    clientSocket.send(index.encode('ascii'))

    # recieve email to view from server or message if index was out of range
    email = clientSocket.recv(2048)
    email = email.decode('ascii')
    # decrypt #
    
    # prints email or message if index was out of range
    print(email)

    return

def client():
    # Server Information
    #serverName = 'cc5-212-19.macewan.ca'#'127.0.0.1' #'localhost'
    serverName = input("Enter the server IP or name: ")
    serverPort = 13000
    
    #Create client socket that useing IPv4 and TCP protocols 
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in client socket creation:',e)
        sys.exit(1)    
    
    try:
        #Client connect with the server
        clientSocket.connect((serverName,serverPort))
        viewEmail(clientSocket)

        # Client is done with server break connection
        clientSocket.close()
        
    except socket.error as e:
        print('An error occured:',e)
        clientSocket.close()
        sys.exit(1)

#----------
client()