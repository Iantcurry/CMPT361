# Sera Vallee, Ian Curry, Sage Jurr, John Divinagracia
# CMPT 361 
# Group Project

import json
import socket
import os,glob, datetime
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# View inbox subprotocol
#
# Parameters:
#       connectionSocket -> connection socket
#       clientUsername -> client's username
#
# Returns:
#       None
#
def viewInbox(connectionSocket, clientUsername):
    sortedInbox = getInbox(clientUsername)

    # Change email list to JSON, encrypt then send
    emailsJSON = json.dumps(sortedInbox)
    encryptedEmails = encrypt(emailsJSON)
    
    # Make sure to use decrypt, then use json.loads() to change
    # JSON back to list
    connectionSocket.send(encryptedEmails)

    # Wait for OK
    decrypt(connectionSocket.receive(2048))

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

def printEncMsg(encMsg, name=''):
    if name != '':
        print("Encrypted message received from " + name + ": " + str(encMsg))
    else:
        print("Encrypted message received: " + str(encMsg))

def printDencMsg(decMsg, name=''):
    if name != '':
        print("Decrypted message received from " + name + ": " + decMsg)
    else:
        print("Decrypted message received: " + decMsg)

def randomQuestion(num):
    answer = 0
    string = ''
    x = random.randint(0,100)
    y = random.randint(0,100)
    op = random.randint(1,3)
    if op == 1:                 # + add
        answer = x + y
        string = f'{"Question"}{num}{": "}{x}{" + "}{y}{" ="}'
    elif op == 2:               # - sub
        answer = x - y
        string = f'{"Question"}{num}{": "}{x}{" - "}{y}{" ="}'
    elif op == 3:               # * mult
        answer = x * y
        string = f'{"Question"}{num}{": "}{x}{" * "}{y}{" ="}'

    return answer, string


# Menu option 2
def exam(connectionSocket, name):
    score = 0
    for i in range(1,5):
        qAns, qStr = randomQuestion(i)

        qStr_e = encrypt(qStr)
        connectionSocket.send(qStr_e)

        # Receive file and save it
        ansEntry_e = connectionSocket.recv(32)
        printEncMsg(ansEntry_e, name)
        ansEntry = decrypt(ansEntry_e)
        printDencMsg(ansEntry, name)

        if int(ansEntry) == qAns:
            score = score + 1

    return score


def menu(connectionSocket):
    """Menu: deals with the menu of the application."""

    # Ask for a name and then receive it
    examMsg = "Welcome to examination System"
    examMsg_e = encrypt(examMsg)
    connectionSocket.send(examMsg_e)

    nameMsg = '1Enter the name: '
    nameMsg_e = encrypt(nameMsg)
    connectionSocket.send(nameMsg_e)

    nameEntry_e = connectionSocket.recv(32)
    printEncMsg(nameMsg_e)
    nameEntry = decrypt(nameEntry_e)
    printDencMsg(nameEntry)

    while True:
        score = exam(connectionSocket, nameEntry)

        # Report score
        scoreMsg = "You achieved a score of " + str(score) + "/4"
        scoreMsg_e = encrypt(scoreMsg)
        connectionSocket.send(scoreMsg_e)

        retryMsg = '2Try again? (y/n)'
        retryMsg_e = encrypt(retryMsg)
        connectionSocket.send(retryMsg_e)

        # Get menu select from client
        menuEntry_e = connectionSocket.recv(32)
        printEncMsg(menuEntry_e, nameEntry)
        menuEntry = decrypt(menuEntry_e)
        printDencMsg(menuEntry, nameEntry)

        # Handle menu options
        if menuEntry == "y":
            continue

        else:
            # Break loop, exit menu, server will handle connection closing
            break

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
    """Server: Manages server application."""

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
                # Run Menu that the User interacts with
                menu(connectionSocket)

                # Server terminates client connection
                connectionSocket.close()
                break
            else:
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
