# Sera Vallee, Ian Curry, Sage Jurr, John Divinagracia
# CMPT 361
# Group Project


import json
import socket
import os
import sys
import random
import os, glob, datetime
import sys
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

# GLOBAL VARS
symKey = 0  # symmetric key generated on login
username = ""


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
Views inbox of client
Notes: clientUsername is not needed as this function
  is only usable AFTER the user has logged in

Parameters:
  clientSocket -> connection socket

Returns:
  None
"""


def viewInbox(clientSocket):
    emails = json.loads(decrypt(clientSocket.recv(2048)))

    print(f"{'Index':<10}{'From':<10}{'DateTime':<30}{'Title'}")
    for email in emails:
        print(f"{email[0]:<10}{email[1][6:]:<10}{email[2][15:]:<30}{email[3][7:]}")

    clientSocket.send(encrypt("OK"))

    return None


def viewEmail(clientSocket):
    # recieve and decode
    message = clientSocket.recv(2048)
    message = decrypt(message)

    # Get index of email from user
    index = input("Enter the email index you wish to view: ")

    # encrypt and send #
    index = encrypt(index)
    clientSocket.send(index)

    # recieve email to view from server or error message if index was out of range
    email = clientSocket.recv(2048)
    # decrypt #
    email = decrypt(email)

    # prints email if index in range or error message if index was out of range
    print()  # for spacing
    print(email)

    return


# ----------
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


def login(clientSocket):
    global symKey
    global username 
    username = input("Enter username: ")
    password = input("Enter password: ")
    userPass = username + ',' + password

    # Encrypt and send username and password
    serverPubKey = RSA.import_key(open("server_public.pem").read())
    cipher_rsa = PKCS1_OAEP.new(serverPubKey)
    raw = pad(userPass.encode(), 64)
    userPass_e = cipher_rsa.encrypt(raw)
    clientSocket.send(userPass_e)

    # Receive server response
    loggedIn = False
    response_e = clientSocket.recv(2048)
    try:
        response = response_e.decode('ascii')
        print(response)
    except UnicodeDecodeError as e:
        serverPubKey = RSA.import_key(open(username + "_private.pem").read())
        cipher_rsa = PKCS1_OAEP.new(serverPubKey)
        raw = cipher_rsa.decrypt(response_e)
        symKey = unpad(raw, 64)                         # set global symKey
        loggedIn = True

    return loggedIn

def menu(clientSocket):
    """Client menu handler"""
    while True:
            # get menu message
            menuStr_e = clientSocket.recv(2048)
            menuStr = decrypt(menuStr_e)

            menuSelect = ""
            valid = False
            while True:
                # print menu and get user input
                print(menuStr)
                menuSelect = input()

                # if it is a valid menu entry, allow continue, else keep prompting
                validInputs = ["1", "2", "3", "4"]
                for entry in validInputs:
                    if entry == menuSelect:
                        valid = True
                        break
                if valid:
                    break
                else:
                    print("Invalid entry")

            # encrypt selection and send
            menuSelect_e = encrypt(menuSelect)
            clientSocket.send(menuSelect_e)

            # go to menu option
            if menuSelect == "1":
                # create an email
                # Recieve message request from server
                message_e = clientSocket.recv(1024)
                message = decrypt(message_e)
                print(message)
                
                # Create Mail
                message = createEmail(username)
                message_e = encrypt(message)
                
                # Send mail message
                size = str(len(message_e)) + ';'
                clientSocket.send(size.encode('ascii'))
                clientSocket.send(message_e)
                
                print("The message was sent to the server.\n")
                
                continue
            elif menuSelect == "2":
                # display email inbox
                viewInbox(clientSocket)
                continue
            elif menuSelect == "3":
                # display email contents
                viewEmail(clientSocket)
                continue
            elif menuSelect == "4":
                # terminate connection
                break
def client():
    """Client: manages connection with server."""
    # Server Information
    # serverName = 'cc5-212-19.macewan.ca'#'127.0.0.1' #'localhost'
    serverName = input("Enter the server IP or name: ")
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

        # Attempt to authenticate user
        loggedIn = login(clientSocket)
        # If successfully authenticated, access menu
        if loggedIn:
            menu(clientSocket)

        # Client terminate connection with the server
        clientSocket.close()

    except socket.error as e:
        print('An error occured:', e)
        clientSocket.close()
        sys.exit(1)


# ----------
client()
# testCreateEmail()
