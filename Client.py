# CMPT 361
# Project

def fileUploadHandler(clientSocket):
    # Assuming that the message for the file upload has already been received
    filePath = ''
    while True:
        try:
            fileName = input()
            filePath = os.getcwd() + '/' + fileName
            size = os.stat(filePath).st_size
            outString = fileName + "\n" + str(size)
            sent_size = clientSocket.send(outString.encode('ascii'))
            break
        except FileNotFoundError:
            print("File \'" + fileName + "\' not found. Try again.")

    # Receive acknowledgement ("OK file_size")
    ack = clientSocket.recv(2048).decode('ascii')
    if ack == '':  # Failed to receive ack
        return

    print(ack)

    with open(filePath, 'rb') as f:
        filePart = f.read(2048)
        while(filePart):
            clientSocket.send(filePart)
            filePart = f.read(2048)

        # clientSocket.shutdown(socket.SHUT_WR)
        f.close()


def menuHandler(clientSocket):
    """Menu Handler: handles all communication to and from server."""
    timeOutCount = 0  # number of loops before time out

    while True:
        isMenu = 0
        # Client receives a message from the server it
        message = clientSocket.recv(2048)
        message = message.decode('ascii')

        # Allow a few blank messages before killing client
        if message == '':
            timeOutCount += 1
            continue
        elif timeOutCount == 3:
            break
        else:
            timeOutCount = 0

        # Check if we're in menu
        if message[0] == '1':
            isMenu = 1
            message = message[1:]

            # Print message from server
            print(message)

            # Client send message to the server
            out = str(input())
            if isMenu & (out == '3'):  # Kill Client if menu in menu and input is 3
                clientSocket.send(out.encode('ascii'))
                break

            clientSocket.send(out.encode('ascii'))

        elif message[0] == '2':
            message = message[1:]
            print(message)
            fileUploadHandler(clientSocket)

        else:
            print(message)




def client():
    """Client: manages connection with server."""
    # Server Information
    serverName = input("Enter hostname or IP: ")
    serverPort = 13000

    # Create client socket that useing IPv4 and TCP protocols
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as e:
        print('Error in client socket creation:', e)
        sys.exit(1)

    try:
        # Client connect with the server
        clientSocket.connect((serverName, serverPort))

        # Get login message from server
        message = clientSocket.recv(2048)
        print(message.decode('ascii'))

        username = input()
        clientSocket.send(username.encode('ascii'))

        # Get login response message from server
        message = clientSocket.recv(2048).decode('ascii')
        if message != '200':
            print(message)

        else:
            menuHandler(clientSocket)

        # Client terminate connection with the server
        clientSocket.close()

    except socket.error as e:
        print('An error occured:', e)
        clientSocket.close()
        sys.exit(1)


# ----------
client()
