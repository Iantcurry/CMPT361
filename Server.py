# Sera Vallee, Ian Curry, Sage Jurr, John Divinagracia
# CMPT 361
# Group Project

import json
import socket
import os, datetime
import sys
import random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

import key_generator

# GLOBAL VARS
symKey = 0          # symmetric key generated on login
username = ""       # username of authenticated client


def encrypt(message):
    raw = pad(message.encode(), 16)
    cipher = AES.new(symKey, AES.MODE_ECB)
    encryptedMsg = cipher.encrypt(raw)

    return encryptedMsg


def decrypt(message):
    cipher = AES.new(symKey, AES.MODE_ECB)
    raw = cipher.decrypt(message)
    decryptedMsg = unpad(raw, 16).decode('ascii')

    return decryptedMsg


"""
View inbox subprotocol

Parameters:
      connectionSocket -> connection socket
      clientUsername -> client's username

Returns:
      None
"""
def viewInbox(connectionSocket, clientUsername):
    sortedInbox = getInbox(clientUsername)

    # Change email list to JSON, encrypt then send
    emailsJSON = json.dumps(sortedInbox)
    encryptedEmails = encrypt(emailsJSON)

    # Make sure to use decrypt, then use json.loads() to change
    # JSON back to list
    connectionSocket.send(encryptedEmails)

    # Wait for OK
    decrypt(connectionSocket.recv(2048))


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
        title = listE[index][3][7:]
        fileName = clientName + '_' + title + '.txt'
        filePath = os.path.join(path,clientName, fileName)

        # now opens filePath created and reads correct email
        with open(filePath, "r") as file:
            email = file.read()  # Reads email

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
        ouputfile.write(storedMessage)
        ouputfile.close()

    print("An Email from " + messageList[0][6:] +
      " is sent to " + messageList[1][4:] +
      " has a conent length of " + messageList[3][16:] + ".\n")


def RecieveMailMessage(socket):
    size = ""
    char = ''
    while char != ';':
        char = socket.recv(1).decode('ascii')
        if char != ';': size += char

    recievedBytes = 0
    recievedData = socket.recv(4096)
    recievedBytes = sys.getsizeof(recievedData)

    while (recievedBytes < int(size)):
        recievedData += socket.recv(4096)
        recievedBytes = sys.getsizeof(recievedData)

    return recievedData


def testStoreMessage():
    inputFile = open("multiline.txt", "r")
    message = inputFile.read()
    inputFile.close()

    storeMessage(message)


def login(connectionSocket):
    """
    Attempt to authenticate a user and generate symmetric key

    returns bool loggedIn, True if successfully authenticated
    """
    global symKey
    global username

    # receive encrypted username and password
    usernamePassword_e = connectionSocket.recv(2048)

    # get server private key and make cipher
    serverPrivKey = RSA.import_key(open("server_private.pem").read())
    cipher_rsa = PKCS1_OAEP.new(serverPrivKey)
    # decrypt, decode to ascii, and split into username and password
    raw = cipher_rsa.decrypt(usernamePassword_e)
    userPass = unpad(raw, 64).decode('ascii').split(',')

    with open("user_pass.json", 'r') as f:
        authUsers = json.load(f)
        f.close()

    # authenticate user
    loggedIn = False
    for user in authUsers:
        if (userPass[0] == user) & (userPass[1] == authUsers[user]):
            loggedIn = True
            username = user

    message = ""
    if loggedIn:
        # Generate and encrypt symmetric key with client public key
        symKey = get_random_bytes(32) # AES 256
        clientPubKey = RSA.import_key(open(username + "_public.pem").read())
        cipher_rsa = PKCS1_OAEP.new(clientPubKey)
        raw = pad(symKey, 64)

        message = cipher_rsa.encrypt(raw)
        print("Connection Accepted and Symmetric Key generated for client: " + username)
    else:
        # dump session key to prevent accidental usage
        symKey = -1
        message = "Invalid Username or Password".encode()
        print("The received information: " + username + "is invalid (Connection Terminated).")

    connectionSocket.send(message)  # Send appropriate message if logged in or not

    return loggedIn


def menu(connectionSocket):
    """Menu: deals with the user menu of the application."""

    while True:

        menuStr = '''
        Select operation:
        \t1) Create and send an email
        \t2) Display the inbox list
        \t3) Display the email contents
        \t4) Terminate the connection
        '''
        menuStr_e = encrypt(menuStr)
        connectionSocket.send(menuStr_e)

        menuSelect_e = connectionSocket.recv(2048)
        menuSelect = decrypt(menuSelect_e)

        # Handle menu options
        if menuSelect == "1":
            # Create and send and email
            # Send Message asking for email
            sendEmail_e = encrypt("Send the Email\n")
            connectionSocket.send(sendEmail_e)

            # Recieve email message (could be quite large)
            message_e = RecieveMailMessage(connectionSocket)
            message = decrypt(message_e)

            # Store message as email
            storeMessage(message)

        elif menuSelect == "2":
            # Display inbox
            viewInbox(connectionSocket, username)

        elif menuSelect == "3":
            # Display email contents
            emailList = getInbox(username)
            viewEmail(emailList, username, connectionSocket)

        elif menuSelect == "4":
            # Break loop, exit menu, server will handle connection closing
            print("Terminating connection with " + username)
            break

        else:
            # Invalid entry, should never happen
            print("Something went wrong - Menu")
            break


def server():
    """Server: Manages server application."""

    # Check that keys have been generated, create them if not
    if not os.path.exists("server_private.pem"):
        key_generator.gen_all_keys()

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
            c_pid = os.fork()
            if c_pid == 0:
                serverSocket.close()

                # Try to log in user, assigns symKey a username global vars
                loggedIn = login(connectionSocket)

                # Run Menu that the User interacts with
                if loggedIn:
                    menu(connectionSocket)


                # Server terminates client connection
                connectionSocket.close()
                break
            else:
                connectionSocket.close()
                concurrent += 1
                continue

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
        #     serverSocket.close()
        #     sys.exit(1)


# -------
server()
#testStoreMessage()
