import socket
import os
import sys
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def viewEmail(clientName):
    message = "the server request email index"
    # encrypt #
    connectionSocket.send(message)
    
    # Recieve index from client
    index = connectionSocket.recv(2048)
    # decrypt #
    
    # must build filePath as it's unique per client
    filePath = "\\" + clientName + "\\list.txt" 
    with open(filePath, "r") as file:
        listE = file.read() # Read list of emails 
    print(listE)
    
    if index < len(listE) - 1: # ensures index in range so it doesn't crash
        filepath = "" #(clears incase old filepath is really long and ensures we completely overwrite it)
        filePath = "\\" + clientName + "\\" + listE[index]
        with open(filePath, "r") as file:
            email = file.read() # Reads email
        # encrypt email
        connectionSocket.send(email)
    else: 
        # if index not in range let user know
        message = "Index out of range, there is no email with that index"
        # encrypt #
        connectionSocket.send(message)
   
    return

def server():
    # Server port
    serverPort = 13000
    
    # Create server socket that uses IPv4 and TCP protocols 
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in server socket creation:',e)
        sys.exit(1)
    
    # Associate 12000 port number to the server socket
    try:
        serverSocket.bind(('', serverPort))
    except socket.error as e:
        print('Error in server socket binding:',e)
        sys.exit(1)        
        
    print('The server is ready to accept connections')
        
    # The server can only have one connection in its queue waiting for acceptance
    serverSocket.listen(5)
        
    while 1:
        try:
            # Server accepts client connection
            connectionSocket, addr = serverSocket.accept()        
            pid = os.fork()
            
            # If it is a client process
            if  pid == 0:               
                serverSocket.close() 
                viewEmail('client1')
                
                # Client is done with server break connection
                connectionSocket.close()
                
                return
            
            # Parent doesn't need this connection
            connectionSocket.close()
            
        except socket.error as e:
            print('An error occured:',e)
            serverSocket.close() 
            sys.exit(1)        
        except:
            print('Goodbye')
            serverSocket.close() 
            sys.exit(0)
            
        
#-------
server()




''' For my own notes to keep strings nicely space out
# Starts compiling results message
message = "\n\nName \t\t Size(Bytes) \t\t Upload Date and Time\n"

# # Constructs string till all keys cycled and sends
for k in keys:
    message += "%-16s %-23s %-5s\n"%(k,str(d[k]["size"]),str(d[k]["time"]))
connectionSocket.send(message.encode('ascii'))
'''