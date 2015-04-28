import os

block_time = 60


def get_credential():
    credential={}
    file = open(os.getcwd()+"/credential.txt",'r')
    all_file = file.readlines()

    for line in all_file:
        tmp = line.split()
        credential[tmp[0]] = tmp[1]
    file.close()

    return credential


def initial_block(credential):  # block, key is username, item is the time it is blocked
    block={}
    for i in credential.keys():
        block[i]= -1 * block_time
    return block


def initial_message_cache(credential):  # message_cache, key is the username, item is the message
    message_cache = {}
    for i in credential.keys():
        message_cache[i] = []
    return message_cache


def initial_block_list(credential):
    block_list = {}
    for i in credential.keys():
        block_list[i] = []
    return block_list


credential = get_credential()
block = initial_block(credential)   # log in block
message_cache = initial_message_cache(credential)
online_list={}
block_list=initial_block_list(credential)  # message block

if __name__ == "__main__":
    a=1
# credential is a list, key is the username, value is the password
# online_list is a list, key is the username, value is tupleip address