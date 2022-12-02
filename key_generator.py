from Crypto.PublicKey import RSA
import json


def client_gen_key_pair(username):
    gen_rsa_key_pair(username + "_private.pem", username + "_public.pem")
    return


def server_gen_key_pair():
    gen_rsa_key_pair("server_private.pem", "server_public.pem")
    return


def gen_rsa_key_pair(privateFilename, publicFilename):
    # Generate key pair
    key = RSA.generate(2048)

    # Save private key
    privKey = key.export_key()
    privFile = open(privateFilename, 'wb')
    privFile.write(privKey)
    privFile.close()

    # Save public key
    pubKey = key.public_key().export_key()
    pubFile = open(publicFilename, 'wb')
    pubFile.write(pubKey)
    pubFile.close()

    return


def gen_all_keys():
    """Run once before using server or client and distribute keys accordingly"""
    server_gen_key_pair()

    # get usernames from file
    with open("user_pass.json", 'r') as f:
        users = json.load(f)

    # create user key pairs
    for user in users:
        client_gen_key_pair(user)

    return

gen_all_keys()
