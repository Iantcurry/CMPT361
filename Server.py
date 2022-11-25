# Sera Vallee
# 3045024
# CMPT 361
# L7

import socket
import sys
import os
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


# -------
server()
