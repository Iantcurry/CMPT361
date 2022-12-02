# Sera Vallee, Ian Curry, Sage Jurr, John Divinagracia
# CMPT 361
# Group Project

import json
import socket
import os,glob, datetime
import sys
import os
import sys
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

#def makeEmailList():

#    return
def viewEmail(listE, clientName, connectionSocket):
    message = "the server request email index"
    # encrypt #
    connectionSocket.send(message.encode('ascii'))

    # Recieve index from client
    index = connectionSocket.recv(2048)
    index = index.decode('ascii')
    index = int(index)
    index -= 1 # user will input index 1 to view item at index 0
    # decrypt #
    '''
    We have decided to scan client's email folder to create list each time instead of keeping a list in a text file.
    But wanted to keep this here incase we want to switch to that implmentation
    # must build filePath as it's unique per client
    # filePath = "\\" + clientName + "\\list.txt" 
    # with open(filePath, "r") as file:
    #    listE = file.read() # Read list of emails 
    #print(listE)
    '''

    if index < len(listE) and index >= 0: # ensures index in range so it doesn't crash
        # must build filePath as it's unique per client
        path = "./"
        filePath = os.path.join(path,clientName, listE[index])
        # print(str(filePath))
        with open(filePath, "r") as file:
            email = file.read() # Reads email
        # encrypt email
        connectionSocket.send(email.encode('ascii'))
    else:
        # if index not in range let user know
        message = "Index out of range, there is no email with that index"
        # encrypt #
        connectionSocket.send(message.encode('ascii'))

    #print(str(index))
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

    concurrent = 0
    while True:
        # The server can only have 1 connection in its queue waiting for acceptance
        serverSocket.listen(5)

        try:
            if concurrent > 5:
                os.wait()
                concurrent -= 1
            # Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            pid = os.fork()

            # If it is a client process
            if  pid == 0:
                serverSocket.close()
                viewEmail(['email1.txt', 'email2.txt'], 'client1', connectionSocket)

                # Client is done with server break connection
                connectionSocket.close()
                break
            else:
                concurrent += 1
                continue

            # Parent doesn't need this connection
            connectionSocket.close()

        except socket.error as e:
            print('A client socket error occurred: ', e)
            continue

        except KeyboardInterrupt as e:
            serverSocket.close()
            sys.exit(0)

        # except Exception as e:
        #     trace = e.__traceback__.tb_lineno
        #     print('Non-Socket exception occurred: ', e)
        #     print("In: ", trace)
            # serverSocket.close()
            # sys.exit(0)


def storeMessage(message):
    messageList = message.split('\n', 4)

    recipientList = messageList[1].split(';')
    recipientList[0] = recipientList[0][4:]

    timeStr = "Time and Date: " + (datetime.datetime.now()).strftime("%d/%m/%Y %H:%M:%S") + "\n"

    storedMessage = (messageList[0] + "\n" +  # From
                     messageList[1] + "\n" +  # To
                     timeStr +                # Timestamp
                     messageList[2] + "\n" +  # Title
                     messageList[3] + "\n" +  # Content Length
                     messageList[4])          # Conent

    filename = messageList[0][6:] + "_" + messageList[2][7:] + ".txt"

    for name in recipientList:
        outfilepath = os.getcwd() + "/" + name + "/" + filename
        ouputfile = open(outfilepath, "w")
        ouputfile.write(message)
        ouputfile.close()


def testStoreMessage():
    inputFile = open("multiline.txt", "r")
    message = inputFile.read()
    inputFile.close()

    storeMessage(message)

# -------
server()
#testStoreMessage()




''' For my own notes to keep strings nicely space out
# Starts compiling results message
message = "\n\nName \t\t Size(Bytes) \t\t Upload Date and Time\n"

# # Constructs string till all keys cycled and sends
for k in keys:
    message += "%-16s %-23s %-5s\n"%(k,str(d[k]["size"]),str(d[k]["time"]))
connectionSocket.send(message.encode('ascii'))
'''
