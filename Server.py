# CMPT 361
# Project

import socket
import sys
import json
from datetime import datetime

# Menu option 1
def metadataView(connectionSocket):
    """SearchPB: Performs search function of application."""

    with open('Database.json', 'r') as fjson:
        try:
            fs = json.load(fjson)
        except Exception:
            fs = {}
        fjson.close()

    tableStr = "Name".ljust(20) + "Size(Bytes)".ljust(20) + "Upload Date and Time\n"
    for item in fs:
        tableStr += item.ljust(20) + str(fs[item]["size"]).ljust(20) + fs[item]["date"] + '\n'

    connectionSocket.send(tableStr.encode('ascii'))

    return fjson.closed

# Menu option 2
def fileUpload(connectionSocket):
    """addPBEntry: Adds a new entry or number to existing entry in phonebook."""

    with open('Database.json', 'r+') as fjson:
        try:
            fs = json.load(fjson)
            fjson.seek(0)
        except Exception as e:
            fs = {}

        # Ask for a name and then receive it
        nameMessage = '2Enter the name: '
        connectionSocket.send(nameMessage.encode('ascii'))
        metaEntry = connectionSocket.recv(2048).decode('ascii')
        currDate = str(datetime.now())

        # if something went wrong, kill subroutine
        if metaEntry == '':
            return

        fileMeta = metaEntry.split("\n")  # Split entry into name and size as in [0] and [1] respectively
        name = fileMeta[0]
        fileSize = int(fileMeta[1])

        # Receive uploaded
        with open(name, 'wb') as uploadF:
            # Send file upload acknowledgement
            ackMessage = 'OK ' + str(fileSize)
            connectionSocket.send(ackMessage.encode('ascii'))

            # Receive file and save it
            filePart = connectionSocket.recv(2048)
            revceivedBytes = 0
            while True:
                uploadF.write(filePart)  # Write uploaded file
                revceivedBytes += len(filePart)
                if revceivedBytes >= fileSize:
                    break;
                filePart = connectionSocket.recv(2048)


            uploadF.close()

            # Add file metadata to file system
            metadata = {"size": fileSize, "date": currDate}
            fs[name] = metadata

            fjson.write(json.dumps(fs))
            fjson.truncate()

        fjson.close()


    return


def fileSystemMenu(connectionSocket):
    """Menu: deals with the menu of the application."""
    while True:
        # Print menu selection message
        menuMessage = "1\n\nPlease select the operation: \n1) View uploaded files information\n" \
                      "2) Upload a file \n3) Terminate the connection\nChoice:"
        connectionSocket.send(menuMessage.encode('ascii'))

        # Get menu select from client
        menuEntry = connectionSocket.recv(2048).decode('ascii')
        menuEntry = int(menuEntry)

        # Handle menu options
        if menuEntry == 1:
            metadataView(connectionSocket)
            continue

        elif menuEntry == 2:
            fileUpload(connectionSocket)
            continue

        elif menuEntry == 3:
            # Break loop, exit menu, server will handle connection closing
            break




def server():
    """Server: Manages server application."""
    open("Database.json", 'w').close()

    # Server port
    serverPort = 13000

    # Create server socket that uses IPv4 and TCP protocols
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        #print('Error in server socket creation:', e)
        sys.exit(1)

    # Associate 12000 port number to the server socket
    try:
        serverSocket.bind(('', serverPort))
    except socket.error as e:
        #print('Error in server socket binding:', e)
        serverSocket.close()
        sys.exit(1)

    #print('The server is ready to accept connections')

    while True:
        # The server can only have one connection in its queue waiting for acceptance
        serverSocket.listen(1)
        try:
            # Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            #print(addr, '   ', connectionSocket)

            introMessage = 'Welcome to our system.\nEnter your username: '
            connectionSocket.send(introMessage.encode('ascii'))

            # Get menu select from client
            userEntry = connectionSocket.recv(2048)
            userEntry = userEntry.decode('ascii')

            # Incorrect Username
            if userEntry != 'user1':
                ejectMessage = 'Incorrect username. Connection Terminated.'
                connectionSocket.send(ejectMessage.encode('ascii'))
                connectionSocket.close()
                continue
            else:
                loginCode = "200"
                connectionSocket.send(loginCode.encode('ascii'))

            # Run Menu that the User interacts with
            fileSystemMenu(connectionSocket)

            # Server terminates client connection
            connectionSocket.close()

        except socket.error as e:
            print('A client socket error occurred: ', e)
            continue

        except KeyboardInterrupt as e:
            serverSocket.close()
            sys.exit(0)

        except Exception as e:
            trace = e.__traceback__.tb_lineno
            print('Non-Socket exception occurred: ', e)
            print("In: ", trace)
            # serverSocket.close()
            # sys.exit(0)


# -------
server()
