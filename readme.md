Name: Xingying Liu
UNI: xl2493

-----------------------------------------------------
         |       Computer Networks    |
         |           Project 1        |
-----------------------------------------------------
python version: 2.7.6
*****************************************************
Design and structure:

This chat room do all the basic functions mentioned in the lab manual, plus one bonus function, P2P Privacy and Consent.
I didn't manage to do the client GUI and Guaranteed Message Delivery in bonus part.

In server, there is one listen socket, it will always be listening if there is a connection. If there is, it will open a thread to deal with the message. And once handled, the thread will be closed immediately. The message can have many forms. It can be message request, or check password request, or get address request...... All these messages can be split into two parts. One part requires immediate reply, one does not. For the ones requires immediate reply, like check password, getaddress. The connection will not be closed until the server gives a reply. And usually, the server will reply immediately. And for the ones don't requires immediate reply, like message request, The connection will be closed right after the message got. And then the server will append the reply message in the message cache so that the server center can deal with it.

There are also two threads in server, one thread for sending(sending center). The sending center will always check if there are any message in the message cache for online users. If there is, the sending center will send all the message to the client. The server write down the address of all the online users. So no worry if it can't find the user. If the user is not online but there are some message for him/her in the message cache, the sending center will not sent it until him/her online.

The other thread is for checking heartbeat. It will always check if any client has not send heartbeat to the server in the late 31 seconds. Here, the client will sent heartbeat every 30 secs. But we want one secs more to allow for the server processing time or any possible delay. The users last heartbeat was write down by the "serve_the_message" thread.

In client, there are three threads. Sending, receiving, and heartbeat. "Sending" is for getting the user's input and then sent relevant request to server. The "sending" thread will wrap the user's input into a form can be accepted by the server. "receiving" is a thread for listening whether there is a connection. The connection can be from the server, or, in the P2P case, from another user. The "heartbeat" thread is simply for sending heartbeat to server every 30 seconds.

The data I used is all in data.py.

"credential" stores accounts. "credential" is a dict. Key is all registered username, item is password.

"block" stores block time. "block" is a dict. Key is all registered username, item is the time it is blocked when log in.

"message_cache" stores unsent messages. It is a dict. Key is all the registered username, item is a list for all the unsent message for that user.

"online_list" stores online user's address and their last active time. It is a dict. Key is username, item is a list. The length of the list is 2. The first item in the list is it's (IP, port), a tuple. The second item is an number representing its last active time.

"block_list" stores black list. It is a dict. Key is username, item is a list of his/her block target.

****************************************************
How to run:
Does not require makefile.
Run in terminal, under the project directory. With the credential.txt!
Run server: python server.py <server_port>
Run client: python client.py <server_ip> <server_port>

Example:
Run server: python server.py 4119
Run client: python client.py 192.168.0.102 4119

****************************************************
How to use:
Basic Client/Server Model:
1. User authentication
    Just type in username and password as indicated.
    Any space after the username or password will be neglected.
    Wrong format will be checked.
    After typing three wrong password, the user will be blocked for 30 secs. Even if he/she try to log in by another IP.

Example 1:  Successfully login
Xingyings-MacBook-Pro:chatroombasic Michelle$ python client.py 192.168.0.102 4119
Please enter username:
columbia
Please enter password:
116bway
You have successfully logged in.

Example 2:
Xingyings-MacBook-Pro:chatroombasic Michelle$ python client.py 192.168.0.102 4119
Please enter username:
columbia
Please enter password:
116bway
You have successfully logged in.
logout
Please enter username:
colu
Wrong username.
Please enter username:
columbia
Please enter password:
11
Please enter password:
11
Please enter password:
11
You have entered wrong password three times. You will be blocked for 30 seconds.
Please enter username:
columbia
Please enter password:
116bway
You are still blocked, please try again later
Please enter password:
------------------------------------------------------------
2. Message exchange
Format: message <target> <yourmessage>

Example:
@seas: message columbia hi
@columbia: seas: hi
------------------------------------------------------------
3. Multiple clients support
The chat room support multiple clients.
------------------------------------------------------------
4. Heartbeat
It is done automatically. User don't need to send heartbeat manually.
Once the user logout, press Ctrl-C, or force close the chat window. The heartbeat will stop.
------------------------------------------------------------
5. Blacklist
Format: block <target>    unblock<target>
If you try to block yourself, or try to unblock someone not in your blacklist, the server will send message to you.
If A has blocked B, B can't send message to A. Also, B can't getaddress A.
------------------------------------------------------------
6. Offline messaging
Offline messaging supported.
------------------------------------------------------------
7. Broadcast
Format: broadcast <your_message>
Broadcast will display the message on everyone online, as long as he/she doesn't block you.
The message will not be displayed in your own window.
------------------------------------------------------------
8. Display current users
Format: online
------------------------------------------------------------
9. Logout
Format: logout
Your account will be logged out. But the client is not closed.
You can go on and login again.
------------------------------------------------------------
10. Graceful exit using control + c
Format: control + c
Your client will be closed. It is different from logout.
------------------------------------------------------------
11. Basic P2P Model 
1. Obtain online user’s IP address
Format: getaddress <target>

Example:
If seas want to get columbia's address.
@seas: getaddress columbia
request sent

@columbia: Do_you_agree to have a private talk with seas? Y seas/N seas
Y seas

@seas: got address!
columbia 192.168.0.102 59316
------------------------------------------------------------
12. Offline report
Yes, the chat room do offline report.

Example:
"facebook is not online. Can't get the address."
"Connect failed. Maybe the user's ip has changed.
You may type: message <username> <message> to leave an offline message."
------------------------------------------------------------
13. P2P message exchange
Format: private <target> <your_message>
************************************************************

To improve:
Permanent link between P2P message? 
Message storage?  FIFO or dict(hash) 
