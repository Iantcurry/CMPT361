import socket
import os,glob, datetime
import sys
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def getKey():
    f = open("key", 'rb')
    key = f.read()
    f.close()

    return key

def encrypt(message):
    key = getKey()
    raw = pad(message.encode(), 32)
    cipher = AES.new(key, AES.MODE_ECB)
    encryptedMsg = cipher.encrypt(raw)

    return encryptedMsg

def decrypt(message):
    key = getKey()
    cipher = AES.new(key, AES.MODE_ECB)
    raw = cipher.decrypt(message)
    decryptedMsg = unpad(raw, 32).decode('ascii')

    return decryptedMsg

def viewEmail(clientSocket):
    # recieve and decode
    message = clientSocket.recv(2048)
    message = decrypt(message)
    
    # Get index of email from user
    index =  input("Enter the email index you wish to view: ")
    
    # encrypt and send #
    index = encrypt(index)
    clientSocket.send(index)

    # recieve email to view from server or error message if index was out of range
    email = clientSocket.recv(2048)
    # decrypt #
    email = decrypt(email)
    
    # prints email if index in range or error message if index was out of range
    print() # for spacing
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