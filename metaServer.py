


#Meta Server:
    #this program will create a server to
    # send information to new peers about
    #p2p network topology.

import socket
from random import randint
import _thread as thread
from time import sleep
import select
import sys


# -- global variables
id = 'Meta'
ip = '127.0.0.1'
p = 50000  #META DATA Server Port
MESSAGE = ''
BUFFER_SIZE = 1024
cache = [] #cache format: [[id,ip,port]]


#-----------------------------------------------------
#function to use as thread to stop program
#-----------------------------------------------------
def stopProgram(threadName):

    while (1):
        input = select.select([sys.stdin], [], [], 1)[0]
        if input:
            value = sys.stdin.readline().rstrip()
            if (value == "Stop" ):
                print ("Exiting")
                sys.exit(0)
            else:
                continue
        else:
            continue

#-----------------------------------------------------
#makes a socket to use, takes port as input (0 = random) and ip number
#-----------------------------------------------------
def makeSocket(ipNum,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 ) # this keeps the port open after closing

    s.bind((ipNum, port))  #use loopback IP  '127.0.0.1' #use port 5000
    s.listen()
    return (s)


#-----------------------------------------------------
#this functiomn can be multiThreaded and will responded to requests to the p2p network
#by sending the whole cache to the peer
#-----------------------------------------------------

def listen(threadName,cache,s):

    print(thread.get_ident())
    count = 0

    while(1):
        print('-----------------------------------------------')
        print('\nNumber of requests: ',count)
        count +=1

        conn , addr = s.accept()     # returns tuple of socket objects and a address of connection

        # Connected to <Incoming Server ID>
        msgRcv = conn.recv(BUFFER_SIZE)
        msgRcv = msgRcv.decode()
        msgRcv = eval(msgRcv)


        print ('Connected to server ID : ',msgRcv[0], ' with address: ', addr[0] ,' on Port:' , addr[1] )

        conId = msgRcv[0]
        p2pFlag = msgRcv[1]
        print(p2pFlag)

        #check if p2p connection is wanted
        if (p2pFlag != 'p2p'):
            print('***Invalid Flag***')
            reply = 'ERROR'
            conn.send(reply.encode())
            continue

        else:
            print('***Valid Flag***')

        peerConnected = False


        #there is nothing in the cache

        if(len(cache) == 0):
            print('Nothing in cache')
            while(peerConnected == False):
                msg='first'
                conn.send(msg.encode())

                msgReply = conn.recv(BUFFER_SIZE)
                msgReply = msgReply.decode()
                if (msgReply == 'connected'):

                    peerConnected == True
                    cache.append([msgRcv[0],addr[0],addr[1]])#add peer to the cache
                    break





        #there is something in the cache
        else:
            print('sending cache')
            while(peerConnected == False):
                cacheStr = str(cache)
                conn.send(cacheStr.encode())
                sleep(1)
                msgReply = conn.recv(BUFFER_SIZE)
                msgReply = msgReply.decode()
                if (msgReply == 'connected'):
                    peerConnected == True
                    cache.append([msgRcv[0],addr[0],addr[1]])#add peer to the cache

                    break

        print('Current Cache:',cache)




def main(cache):

    shutdown = False
    s = makeSocket(ip,p)
    print('MetaServer is now listening')

    threadCount = 0

    while (not(shutdown)): #run until shutdown is set to True or 'Stop' is inputted
        try:
            # thread.start_new_thread( stopProgram, ('stopper',) ) #CAUSING ERROR

            #allow a certian amount of threads to listen for p2p requests from peers
            if(threadCount < 1):
                print('new thread starting up')
                thread.start_new_thread( listen, (str(threadCount),cache,s) )
                threadCount +=1



        except KeyboardInterrupt:
            print('\nShutting Down Meta Server...')
            shutdown = True
            s.close()
            break



main(cache)
