import socket
import thread
import time
import sys
block_time = 30
logout_sig = 0
my_friends={}


def connect_server(message, (host, port)):  # open a socket, send message, close socket
    #print("Send this message to server: "+message)
    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(message)
    s.close()


def connect_server_until_reply(message, (host, port)):  # open a socket, send message, wait for reply,close socket
    #print("Send this message to server: "+message)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(message)
    reply = s.recv(1024)
    #print("Server reply: "+reply)
    s.close()
    return reply


def receiving(s):
    global logout_sig
    while logout_sig == 0:
        connection, addr = s.accept()
        got = connection.recv(1024)
        connection.close()
        if got[0:5]=="print":
            print(got[6:])
        else:
            got = got.split()
            if got[0]=="logout":
                print("Someone else has successfully logged in by your username, you are logged out.")
                logout_sig = 1
            elif got[0]=="private":
                print(got)
            elif got[0] == "refused":
                print(got[1]+" refused to give you address.")
            elif got[0] == "address": # Format: address <the one who consented> <ip> <port>
                print("got address!")
                friend = got[1]
                my_friends[friend] = (got[2], int(got[3]))
                print(friend+' '+got[2]+' '+got[3])
    return


def sending(username):
    global logout_sig
    while True:   # The function returns when get an logout from user
        command = raw_input().strip()  # command is user input
        if len(command) == 0:
            return
        else:
            #print("command "+command+" received.")
            command = command.split()

        if command[0] == "online":
            if len(command) != 1:
                print("Wrong Format.")
            else:
                message = "online"
                reply = connect_server_until_reply(message, (server_host,server_port))
                print(reply)

        if command[0] == "message":
            if len(command) <= 2:
                print("Wrong Format.Should be message <username> <your message>")
            elif command[1] == username: print("You are sending message to yourself.")
            else:
                message = "message " + username # message to server. Format message <username> <target_name> <message>
                del command[0]
                for word in command:
                    message = message + ' ' + word
                reply = connect_server_until_reply(message,(server_host, server_port))
                if reply == "wrong target":
                    print("The user you want to speak to doesn't exist.")
                if reply == "blocked":
                    print("Your message could not be delivered as the recipient has blocked you.")

        if command[0] == "logout":
            connect_server("logout "+username, (server_host, server_port))  # Format logout <username>
            logout_sig=1  # set the global to 1. To end all the other threads.
            return  # return the function.  hence end the thread

        if command[0] == "block":
            if len(command) != 2:
                print("Wrong format. Should be block <username>")
            else:
                target = command[1]
                if target == username: print("You can't block yourself.")
                else:
                    message = "block "+username+' '+target  # Format block <username> <block target>
                    reply = connect_server_until_reply(message, (server_host, server_port))
                    if reply == "user not exist":
                        print("User "+target+" doesn't exist.")
                    else:
                        print("User "+target+" has been blocked")

        if command[0] == "unblock":
            if len(command) != 2:
                print("Wrong format. Should be unblock <username>")
            else:
                target = command[1]
                if target == username: print("You can't unblock yourself.")
                else:
                    message = "unblock "+username+' '+target  # Format unblock <username> <unblock target>
                    reply = connect_server_until_reply(message, (server_host, server_port))
                    if reply == "user not exist":
                        print("User "+target+" doesn't exist.")
                    elif reply  == "not blocked before":
                        print("User "+target+" was not blocked by you before.")
                    else:
                        print("User "+target+" has been unblocked")

        if command[0] == "broadcast":
            if len(command)<2:
                print("Wrong format. Should be broadcast <message>")
            else:
                message = "broadcast "+username  # Format broadcast <username> <message>
                del command[0]
                for word in command:
                    message = message+' '+word
                connect_server(message, (server_host, server_port))

        if command[0] == "getaddress":
            if len(command)!=2:
                print("Wrong format. Should be getaddress <username>")
            else:
                target = command[1]
                message = "getaddress "+username+' '+target  # Format: getaddress <username> <target>
                reply = connect_server_until_reply(message,(server_host,server_port))
                if reply == "wrong target":
                    print(reply)
                elif reply == "not online":
                    print(target+" is not online. Can't get the address.")
                elif reply == "blocked":
                    print(target+" has blocked you. You can't get the address.")
                elif reply == "request sent":
                    print(reply)

        if command[0]=='Y'or command[0]=='N': # message from client. Format: Y/N username target
            message = command[0]+' '+username+' '+command[1]
            connect_server(message, (server_host, server_port))

        if command[0] == "private":
            if len(command)<3:
                print("Wrong format. Should be private <username> <message>")
            else:
                target = command[1]
                if target not in my_friends:
                    print("You should get address first. Format: getaddress <username>")
                else:
                    message = "private "+username+':'
                    del command[0:2]
                    for word in command:
                        message = message+' '+word
                    try:
                        connect_server(message,my_friends[target])
                    except:
                        print("Connect failed. Maybe the user's ip has changed.")
                        print("You may type: message <username> <message> to leave an offline message.")



def login():
    flag = 0
    while flag != 1:
        while True:
            print("Please enter username:")
            username = raw_input().strip()
            if len(username.split())!=1:
                print("Wrong username.")
            else:
                send_message = "login "+username+' '+my_IP+' '+str(my_port)
                reply = connect_server_until_reply(send_message, (server_host, server_port))
                if reply == 'error 1':
                    print("Wrong username.")
                elif reply == "right username": break

        for i in range(1,4):
            print("Please enter password:")
            password = raw_input().strip()
            if ' ' in password:
                print("Wrong format. Please try again.(This kind of wrong password will not cause block.)")
            else:
                send_message = "check_password "+username+' '+password+' '+str(i)+' '+my_IP+' '+str(my_port)
                reply = connect_server_until_reply(send_message, (server_host, server_port))
                if reply == "still blocked":
                    print("You are still blocked, please try again later")
                elif reply == "wrong password":
                    if i==3: print("You have entered wrong password three times. You will be blocked for 30 seconds.")
                    else: continue
                elif reply == "successfully logged in!":
                    print("You have successfully logged in.")
                    flag = 1
                    break
    return username


def heartbeat(username):  # send heartbeat every 30 secs
    try:
        while logout_sig==0:
            connect_server("heartbeat "+username, (server_host, server_port))  # Format heartbeat <username>
            time.sleep(30)
    except:
        return


def free_port():  # get an free port by s.bind('',0)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    connect, port = s.getsockname()
    s.close()
    return port


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Try again. Format: python client.py <server_ip> <server_port>")
        sys.exit()

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    my_IP = socket.gethostbyname(socket.gethostname())
    my_port = free_port()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((my_IP, my_port))
    s.listen(10)

    try:
        while True:
            logout_sig = 1
            username = login()
            logout_sig = 0


            thread.start_new_thread(sending, (username,))
            thread.start_new_thread(receiving, (s,))
            thread.start_new_thread(heartbeat, (username,))
            while logout_sig == 0:
                pass
    except KeyboardInterrupt:
        print("You pressed Ctrl+C, exit")
        connect_server("logout "+username, (server_host, server_port))  # Format logout <username>
        logout_sig=1
        s.close()
        sys.exit()