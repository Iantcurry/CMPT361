# Sera Vallee
# 3045024
# CMPT 361
# L7

import socket
import sys
import os
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

def exam(clientSocket):
    for i in range(4):
        # get question
        question_e = clientSocket.recv(32)
        question = decrypt(question_e)
        print(question)

        # send user entry
        answer = input()
        answer_e = encrypt(answer)
        clientSocket.send(answer_e)



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
        while True:
            # get first message
            message1_e = clientSocket.recv(32)
            message1 = decrypt(message1_e)
            print(message1)

            message2_e = clientSocket.recv(32)
            message2 = decrypt(message2_e)
            flag = message2[0]
            print(message2[1:])

            # send user entry
            entry = input()
            entry_e = encrypt(entry)
            clientSocket.send(entry_e)

            if flag == '2' and entry != 'y':
                break
            else:
                exam(clientSocket)

        # Client terminate connection with the server
        clientSocket.close()

    except socket.error as e:
        print('An error occured:', e)
        clientSocket.close()
        sys.exit(1)


# ----------
client()
