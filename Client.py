# Sera Vallee, Ian Curry, Sage Jurr, John Divinagracia
# CMPT 361 
# Group Project


import json
import socket
import os,glob, datetime
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# Views inbox of client
# Notes: clientUsername is not needed as this function
#   is only usable AFTER the user has logged in
#
# Parameters:
#   connectionSocket -> connection socket
#
# Returns:
#   None
#
def viewInbox(connectionSocket):
    emails = json.loads(decrypt(connectionSocket.recv(2048)))

    print(f"{'Index':<10}{'From':<10}{'DateTime':<30}{'Title'}")
    for email in emails:
        print(f"{email[0]:<10}{email[1]:<10}{email[2]:<30}{email[3]}")

    connectionSocket.send(encrypt("OK"))

    return None


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

def createEmail(username):
    message = ""
    
    # Get recipeints
    recipients = input("Enter recipient(s) (separated by ;): ")
    
    # Get Title (limit to 100 chars)
    title = input("Enter email title (limit 100 chars): ")
    while (len(title) > 100):
        print("Title is too long, please limit to 100 characters.")
        title = input("Enter email title (limit 100 chars): ")
    
    # Get body Content (limit to 1000000 chars)
    contentLength = 1000001
    while (contentLength > 1000000):
        isFile = input("Would you like to load contents from a file? (Y/N) ")
        
        contents = ""
        if (isFile.upper() == "Y"):
            # get from file
            filename = input("Enter filename: ")
            while (os.path.isfile(filename) == False):
                print("Filename invalid.")
                filename = input("Enter filename: ")
              
            file = open(filename, "r")
            contents = file.read()
            file.close()
        else:
            contents = input("Enter message contents: ")
        contentLength = len(contents)
        if (contentLength > 1000000):
            print("Content too long, limit to 1000000 characters.")
    
    # construct message
    message = ("From: " + username + "\n" +
               "To: " + recipients + "\n" +
               "Title: " + title + "\n" +
               "Content Length: " + str(contentLength) + "\n" +
               "Content:\n" +
               contents)
    
    
    return message

def testCreateEmail():
    message = createEmail("user1")
    print(message)
    output = open("message.txt", "w")
    output.write(message)
    output.close()
    
# ----------
client()
#testCreateEmail()
