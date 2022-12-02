import json
import socket
import os,glob, datetime
import sys
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

# Get inbox, helper function
#
# Parameters:
#   clientUsername -> client's username
#
# Returns:
#   emails -> list of sorted emails
#
def getInbox(clientUsername):
    emails = []

    # Assuming location is in "(client username)/(email).txt"
    for file in os.listdir(clientUsername):
        path = "./"
        filePath = os.path.join(path,clientUsername, file)        
        with open(filePath) as email:
            emailRead = email.read().splitlines()
            
            # Emails will have the following format:
            #   From, To, Timestamp, Title, Content Length, Content.
            #   Each separated by "\n". 
            #
            # Only want From, Timestamp, and Title:
            # Use indices 0, 2, 3 on emailRead
            emails.append([emailRead[0], 
                           emailRead[2], 
                           emailRead[3]])
    
    # Sorts emails by time and date sent
    # emails.sort(key=lambda time: emails[1])

    # Add index to each email
    for i in range(len(emails)):
        emails[i].insert(0, i+1) # adds 1 to the index so for the user it starts 1 one, EX. email 1 should have index 1 not 0.
   
    return emails


def viewEmail(listE, clientName, connectionSocket):
    message = "the server request email index"
    # encrypt and send 

    message = encrypt(message)
    connectionSocket.send(message)
    
    # Recieve index from client and decrpyt
    index = connectionSocket.recv(2048)
    index = decrypt(index)
    
    # Checks if index is a integer if it isn't will notify user
    if index.isdigit() != True:
        message = "Not a valid index, there is no email with that index"
        
        # encrypt and send 
        message = encrypt(message)
        connectionSocket.send(message)        
    index = int(index)
    # minus 1 to remove off by 1 error Example: user will input index 1 to view item at index 0
    index -= 1
    
    # ensures index in range so it doesn't crash, if it isn't notifies user
    if index < len(listE) and index >= 0:
        # must build filePath as it's unique per client
        path = "./"
        
        # Making fileName
        # filename is formatted as "username_title.txt"
        tempL = listE[index][3].split(" ")
        fileName = clientName + '_' + tempL[1] + '.txt'
        filePath = os.path.join(path,clientName, fileName)
        
        # now opens filePath created and reads correct email
        with open(filePath, "r") as file:
            email = file.read() # Reads email
            
        # encrypt email and send to user
        email = encrypt(email)
        connectionSocket.send(email)
    
    else: 
        # if index not in range let user know
        message = "Index out of range, there is no email with that index"
        
        # encrypt and send #
        message = encrypt(message)
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
                emails = getInbox('client1')
                viewEmail(emails, 'client1', connectionSocket)
                #emails = getInbox('client1')
                #print(emails)
                
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