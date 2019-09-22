#Siraj Hassan
#CSCI 4211
#hassa340

#This program creates a peer that can
#join the p2p network, which it gets information
#about by contacting the metaServer at port 50,000


import sys
import socket
from random import randint
import _thread as thread
from time import sleep
# import select


#global variables
conLim = 2 #allowed connections (excluding the one temporary)
id = 0 #custom id based on input
ip = '127.0.0.1'
port = 0
peerList = [] # Peer List: list of two connections (server objects)
broadCastMessage = ['',''] #this list will contain strings to broadcast from sockets to peers
# temp = 0   #one temporary connection for switching (server object)
# shutdown = False
numCon = 0 # keeps count on number of current connections.
numThread = 0
topo = False
root = False
BUFFER_SIZE = 1024



#This function caused issues on OSX
#-----------------------------------------------------
#function to use as thread to stop program
#-----------------------------------------------------
# def stopProgram(threadName):
#
#     while (1):
#
#         input = select.select([sys.stdin], [], [], 1)[0]
#         if input:
#             value = sys.stdin.readline().rstrip()
#
#             if (value == "Stop" ):
#                 print ("Exiting")
#                 sys.exit(0)
#             else:
#                 continue
#         else:
#             continue



#-----------------------------------------------------
#convert peerList to proper format
#-----------------------------------------------------
def convertPeers(plist):
    global id
    i = 0
    newList = []
    while(i < len(plist)):
        newList.append(plist[0])
        i+=1

    str = ('Server ' + str(id) + '| Connections: ' + str(newList))

    if len(plist ==0):
        return('Server ' + str(id) + '| Connections:')

    return(str)



#-----------------------------------------------------
#makes a socket to use, takes port as input (0 = random)
#-----------------------------------------------------
def makeSocket(p=0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 ) # this keeps the port open after closing
    s.bind(('127.0.0.1',p))
    return (s)

#-----------------------------------------------------
# makes a socket and contacts peers to see if they can be connected to.
#-----------------------------------------------------

#contacts peers to see if they can be connected to.
def pingPeer(ip,p):
    global id
    print('pinging potential peer....')
    msg = 'ping from: ' + str(id)
    # print('ping ip:', ip)
    # print('ping port:', p)
    try:
        sTemp = makeSocket()
        sTemp.connect((ip, p))
        sTemp.send(msg.encode())
        sleep(1)  # wait for 1 or 0 response from server, if 1, then it can be joined.

        sTemp.settimeout(2)  #
        msgRcv = sTemp.recv(BUFFER_SIZE) #if no response after certain time, assume no join

        # print(msgRcv)
        sTemp.shutdown(socket.SHUT_RDWR)
        sTemp.close()
        return(1) #we recieved a response from the server we are trying to connect to

    except Exception as e:
         return(0)



#-----------------------------------------------------
#function to use new socket to connect to suggested peer from meta Data server
#This function will also listen for 'topo' calls
#This function is run by a thread called in main
#p2Connect is the port that you are attempting to connect to
# s = socket object
#-----------------------------------------------------
def connPeer(threadName,s,p2Connect):
    global id
    global port
    global ip
    global broadCastMessage
    global numCon
    global topo

    # print('listening/conneted to port: ' , p2Connect)
    msg = 'incoming connection:' + str([id,ip,port]) #send to new peer just once
    s.send(msg.encode())

    while(1):
        print('---------------------')
        sleep(.5)
        #check the broadCastMessage in memory to see if anything needs to be sent to neighbor
        if (broadCastMessage[1] != '' ):

            # print('topo message:', broadCastMessage[1])
            print('topo peer list :',convertPeers(peerList))
            msg = broadCastMessage[1]
            s.send(msg.encode())
            broadCastMessage[1] = ''


        msgRcv = s.recv(BUFFER_SIZE)
        msgRcv = msgRcv.decode()
        numCon += 1

        if('topo' in msgRcv):
            print('topo peer list:' ,convertPeers(peerList))
            broadCastMessage[0] = msgRcv #so other socket can send to neighbors
            broadCastMessage[1] = ''
            sleep(1)




#-----------------------------------------------------
#- This function listens for pings and connection and topo requests
#- multithreaded function, first node in p2p network will have two threads
#- All the rest of the nodes will only run one threads
#-----------------------------------------------------
def listen(threadName,s,conn,addr):
    global numCon
    global numThread
    global peerList
    global broadCastMessage
    global root
    print('listening on port: ' , port)


    while(1):
        print('______________________')

        #recieve messages
        msgRcv = conn.recv(BUFFER_SIZE)
        msgRcv = msgRcv.decode()
        sleep(1)
        if (msgRcv != ''):
            print('message recieved: ',msgRcv)

        #Protocol for dealing with incoming messages below....

        if (broadCastMessage[0] != '' ):
            # print('topo message:', broadCastMessage[0])
            # print('topo peer list :',peerList)
            # print('listen topo')
            msg = broadCastMessage[0]
            conn.send(msg.encode())
            broadCastMessage[0] = ''


        if ('incoming connection:' in msgRcv): #this is a new acceptable connection
            msgRcv = msgRcv.split(':')
            peer = msgRcv[1]              #extract peer info and put into peer list
            peer = eval(peer)
            peerList.append(peer)   #fill peers and their listening ports into a global list
            print('peerList',convertPeers(peerList))

        elif('topo' in msgRcv): #notifiy other socket that it needs to send a topo

            #for root node being 2 listeners
            # print(root)
            if(root == True):
                print(' peer list :',convertPeers(peerList))
                msg = broadCastMessage[1]
                conn.send(msg.encode())
                broadCastMessage[0] = ''

            # print('topo message:', msgRcv)
            print(' peer list :',convertPeers(peerList))


            broadCastMessage[1] = msgRcv #so other socket can send to neighbors
            broadCastMessage[0] = ''
            sleep(.2)


        elif ('ping' in msgRcv):
            if(numCon <=2):
                msg = 'yes'
                conn.send(msg.encode())
                numThread -= 1 #so another connection can be made
                return
            else:
                msg = 'no'
                conn.send(msg.encode())
                numThread -= 1
                return

        else:
            numCon +=1


        #message protocol:

        # print('numcon',numCon)
        #make a protocol function for certain messages.....
        #send out information based on protocol.....



#--------------------------------------------------------------------
#request the MetaData Server to assign a place in the p2p networkself.
#return ip and port to connect to, if same ip and port returned as self, then you are first peer
#----------------------------------------------------------------------------
def requestP2P(s):
    global port
    global id
    global ip

    p2pConnection = False
    port = s.getsockname()[1]
    print('Port being used by this peer:', port)



    # while(p2pConnection == False):  TODO : fix this so it can loop with one port being send at a time


    print('Server ' , id , ' is using port: ' , port  )
    #connect to the metaServer on its port (set to 50,000 for this program)
    succ = s.connect(('127.0.0.1', 50000))
    print('Connection to metaData server successful')

    #IO 3 : enter the p2p command
    flag = input('Please input a "p2p" flag to join the network: ')


    msg = str([id,flag])
    s.send(msg.encode())
    sleep(1)
    msgRcv = s.recv(BUFFER_SIZE)
    msgRcv = msgRcv.decode()

    if (msgRcv == 'ERROR'):
        print('improper flag, please try again..')
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        exit(0)

    if (msgRcv == 'first'):
        print('First node in p2p network')
        tup = ('self','127.0.0.1',port)
        p2pConnection = True
        # break


    else:
        cache = eval(msgRcv) # this should be either the current cache, or a 1(first node in p2p)
        i = 0
        while(i<len(cache)):
            stat = pingPeer(cache[i][1],cache[i][2]) #tells us if peer to connect to is availible
            if (stat == 1):
                tup = (cache[i][0],cache[i][1],cache[i][2])
                p2pConnection = True
                break
            else:
                i+=1



    if (p2pConnection == True):
        print('Connected to p2p network')
        confirmation = 'connected'
        s.send(confirmation.encode())

    else:
        print('Failure to connect to p2p network....')
        tup = (-1,-1,-1)




    s.shutdown(socket.SHUT_RDWR)
    s.close()
    return(tup)




#--------------------------------------------------------
# Main function deals with IO and threading. The function will
# take in parameters, request from the MetaServer to send information,
#then start the listening and connection threads.
#-----------------------------------------------------

def main():
    global peerList
    global numCon
    global id
    global numThread
    global topo
    global broadCastMessage
    global root

    while(1):
        n = input('Please press 1 to add server to p2p network or Press 2 for file download: ')

        if(n == '1'):
            id = input('Enter an ID for the server: ')
            t = input('Enter "topo" so see topology, otherwise, press enter: ')
            if(t == 'topo'):
                topo = True
                break
            else:
                break

        elif(n == '2'):
            print('Sorry, phase 2 of the project is not finished. Do not push 2 agains')
            continue
        else:
            print('IMPROPER input, try again')
            continue

    # topo = True

    if (topo == True):
        broadCastMessage[0] = ('topo')
        broadCastMessage[1] = ('topo')



    # print('------------')
    metaSocket = makeSocket()
    conId,ip,p = requestP2P(metaSocket) #this will return a (id, ip and port to join the network with)
                  #if first node in p2p, start 2 listening functions,
                  #otherwise use given connection in ip and p and 1 listening function.


    if(conId == -1):
        return('shutting down, failed to join network')


    #This means were the first node in the p2p network, have two listening threads run
    elif(conId == 'self'):
        root = True #to signify this is the first node
        shutdown = False

        sListen = makeSocket(port)  #this will have same port as one on MetaData table
        sListen.listen()

        while (not(shutdown)): #run until shutdown is set to True
            try:

                if(numThread < 2):

                    conn , addr = sListen.accept()
                    thread.start_new_thread( listen, (str(numCon),sListen,conn,addr) )
                    numThread +=1


            except KeyboardInterrupt:
                print('\nShutting down peer server...')
                shutdown = True
                sListen.shutdown(socket.SHUT_RDWR)
                sListen.close()
                break


   #This means there is a peer that can be connected to
    else:
        #add Peer to peerList

        shutdown = False
        sListen = makeSocket(port)
        sListen.listen(2)
        sConn = makeSocket()
        sConn.connect((ip,p))

        peerList.append([conId,ip,p])
        print('peerList:',peerList)

        msg = 'connect' #initially notify the peer that it wants to connect
        # sConn.send(msg.encode())

        # print('peers are in network')
        #create a socket to reach out to the given port
        #create a listening thread to recieve information
        while (not(shutdown)): #run until shutdown is set to True
            try:

                if(numThread < 1): #this will be the first thread reach out

                    # print('conn staring up')
                    print('server' , id , 'connecting to server: ', conId, ' via port ',p )
                    thread.start_new_thread( connPeer, (str(numCon),sConn,p) )
                    numThread +=1

                if(numThread < 2): #this thread will wait to accept a connection
                    # print('listen starting up')
                    conn , addr = sListen.accept()
                    thread.start_new_thread( listen, (str(numCon),sListen,conn,addr) )
                    numThread +=1

                    #TODO, LISTEN FOR IO / TOPO

            except KeyboardInterrupt:
                print('\nShutting down peer Server...')
                shutdown = True
                sConn.shutdown(socket.SHUT_RDWR)
                sConn.close()
                sListen.shutdown(socket.SHUT_RDWR)
                sListen.close()
                break





main()
