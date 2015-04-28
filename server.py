import socket
import thread
import data
import time
import client
import sys
lock = thread.allocate_lock()


def check_heartbeat():
    global lock
    while True:
        lock.acquire()
        offline = []
        for user in data.online_list:
            last_active = data.online_list[user][1]
            if time.time() - last_active >= 31: # use 31 sec to allow for the processing time
                offline.append(user)
        for user in offline:   # use two for loops, to avoid change the list in iteration
            user_ip_port = data.online_list[user][0]
          #  client.connect_server("logout", user_ip_port)
            del data.online_list[user]
        lock.release()


def server_send_center():
    global lock
    while True:
        lock.acquire()
        for username in data.online_list: # for all users
            while len(data.message_cache[username]) != 0:
                #print("Send center,",username, ' ', data.message_cache[username])
                (client_host, client_port) = data.online_list[username][0]
                message = data.message_cache[username][0]
                del data.message_cache[username][0]
                client.connect_server(message, (client_host, client_port))  # send message
        lock.release()


def serve_the_message(connection, addr):
    global lock
    got = connection.recv(1024)
    message = got.strip().split()  # the message got from clients
    print("Got this message from client: ", message)

    # login
    if message[0]=="login":  # the message is processed by client server. Format: login <username> <password> <ip> <port>
        name = message[1]
        if name not in data.credential:
            connection.sendall("error 1")  # The user doesn't exist
            print("sent error 1")
        else:
            connection.sendall("right username")
            print("sent right username")

    elif message[0] == "check_password":  # Format: check_password <username> <password> <try time> <ip> <port>
        username = message[1]
        password = message[2]
        try_time = message[3]
        ip = message[4]
        port = int(message[5])
        if time.time() - data.block[username] < data.block_time:  # check block time
            connection.sendall("still blocked")
        elif data.credential[username]!= password:  # check password
            connection.sendall("wrong password")
            if try_time == '3': data.block[username] = time.time()
        else:
            connection.sendall("successfully logged in!")
            print(username+" has successfully logged in.")
            lock.acquire()
            if username in data.online_list:  # If someone has logged in by the username, make him/her logout
                client.connect_server("logout", data.online_list[username][0])
                print("sent logout to "+username+' ',data.online_list[username][0])
                del data.online_list[username]
            data.online_list[username] = [(ip, port), time.time()] # add client to online list, save address
            print("online list: ", data.online_list.keys())  # take the login time as the first heartbeat
            lock.release()

    elif message[0] == "online":
        reply = ''
        for i in data.online_list:
            reply = reply + i + ', '
        connection.sendall(reply)

    elif message[0] == "message": # Format: message <username> <target_name> <message>
        username = message[1]
        target = message[2]
        if target not in data.credential: # check if it is a right target
            connection.sendall("wrong target")
        if username in data.block_list[target]:
            connection.sendall("blocked") # Your message could not be delivered as the recipient has blocked you
        else:
            del message[0:3]
            information = "print "+username + ':'
            for word in message:
                information = information + ' '+word
            data.message_cache[target].append(information) # add the message to message cache
            #print("add information "+information+" to "+target)
            print(data.message_cache[target])

    elif message[0] == "logout": # Format logout <username>
        username = message[1]
        lock.acquire()
        del data.online_list[username]
        lock.release()

    elif message[0] == "block": # Format block <username> <block target>
        username = message[1]
        target = message[2]
        if target not in data.credential:  # check if it's a valid username
            connection.sendall("user not exist")
        else:
            if target not in data.block_list[username]: # add to block list
                data.block_list[username].append(target)
            connection.sendall("User "+target+" has been blocked.")

    elif message[0] == "unblock": # Format unblock <username> <unblock target>
        username = message[1]
        target = message[2]
        if target not in data.credential:  # check if it's a valid username
            connection.sendall("user not exist")
        else:
            if target not in data.block_list[username]:  # check if the user is unblocking someone not in blacklist
                connection.sendall("not blocked before")
            else:
                data.block_list[username].remove(target)  # delete from block list
                connection.sendall("User "+target+" has been unblocked.")

    elif message[0] == "broadcast":  # Format broadcast <username> <message>
        username = message[1]
        information = "print "+username+':'
        del message[0:2]
        for word in message:
            information = information+' '+word
        for user in data.online_list:
            if (username!=user) & (username not in data.block_list[user]): # Doesn't broadcast to the user who broadcast
                data.message_cache[user].append(information)

    elif message[0] == "heartbeat": # Format heartbeat <username>
        username = message[1]
        if username in data.online_list:
            data.online_list[username][1] = time.time()  # use online list to store the last active time

    elif message[0] == "getaddress": # Format: getaddress <username> <target>
        username = message[1]
        target = message[2]
        if target not in data.credential:  # check if it is a valid username
            connection.sendall("wrong target")
        elif target not in data.online_list:  # check if the target is online
            connection.sendall("not online")
        elif username in data.block_list[target]:  # check if target has block the user
            connection.sendall("blocked")
        else: # send request to target   # send request
            tmp_string = "print Do_you_agree to have a private talk with "+username+"? Y "+username+"/N "+username
            client.connect_server(tmp_string, data.online_list[target][0])
            connection.sendall("request sent")

    elif message[0]=='Y' or message[0]=="N":   # message from client. Format: Y/N username target
        username = message[1]
        target = message[2]
        lock.acquire()
        if message[0] == 'Y':  # Y means user agrees to speak with target, so send user's address to target
            user_addr = data.online_list[username][0]
            data.message_cache[target].append("address "+username+' '+user_addr[0]+' '+str(user_addr[1]))
            print(target, ' ',data.message_cache[target])
        elif message[0] == 'N':  # Y means user refuses to speak with target
            data.message_cache[target].append("refused "+username)
            print(target, ' ',data.message_cache[target])
        lock.release()


    connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:  #  check the way it is opened
        print("Try again. Format: python server.py <server_port>")
        sys.exit()

    host = socket.gethostbyname(socket.gethostname())   # set the server host as the local address
    port = int(sys.argv[1])
    print("server IP: "+host+". Server port: "+str(port))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # open a socket for listen
    s.bind((host, port))
    s.listen(10)

    thread.start_new_thread(server_send_center, ())  # sending message to all clients
    thread.start_new_thread(check_heartbeat,())  # check the heartbeat for all clients
    try:
        while True:  # keep listening all the time
            connection, addr = s.accept()
            print("Connected by ", addr)
            thread.start_new_thread(serve_the_message, (connection, addr))  # One thread for one message
    except KeyboardInterrupt:   # capture KeyboardInterrupt
        print("You pressed Ctrl+C, exit")
        s.close()   # close the socket before closed
        sys.exit()


