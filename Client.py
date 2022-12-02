# Sera Vallee, Ian Curry, Sage Jurr, John Divinagracia
# CMPT 361
# Group Project


import json
import socket
import os
import sys
import random
import os,glob, datetime
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def viewEmail(clientSocket):
    message = clientSocket.recv(2048)
    message = message.decode('ascii')
    # decrpyt #

    index =  input("Enter the email index you wish to view: ")
    # encrypt #
    clientSocket.send(index.encode('ascii'))

    # recieve email to view from server or message if index was out of range
    email = clientSocket.recv(2048)
    email = email.decode('ascii')
    # decrypt #

    # prints email or message if index was out of range
    print(email)

    return

def client():
    # Server Information
    #serverName = 'cc5-212-19.macewan.ca'#'127.0.0.1' #'localhost'
    serverName = input("Enter the server IP or name: ")
    serverPort = 13000

    #Create client socket that useing IPv4 and TCP protocols
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in client socket creation:',e)
        sys.exit(1)

    try:
        #Client connect with the server
        clientSocket.connect((serverName,serverPort))
        viewEmail(clientSocket)

        # Client is done with server break connection
        clientSocket.close()

    except socket.error as e:
        print('An error occured:',e)
        clientSocket.close()
        sys.exit(1)

#----------
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
