import socket
import logging
import datetime as dt
import threading
import time
from ahk import AHK
import random
from config import TOKEN, HOT_KEY_PATH, CHANNEL, NICKNAME

from formlayout import fedit


SERVER = 'irc.chat.twitch.tv'
PORT = 6667
ENCODING = 'utf-8'


minutes = 3



# # I think I might want to use queues instead of modifying global variables
### https://stackoverflow.com/questions/19790570/using-a-global-variable-with-a-thread
# from queue import Queue


#  maybe I should utilize threading Locks?







# global variables
message = ""
user = ""
continueRunning = True

ahk=AHK(executable_path=HOT_KEY_PATH)


#make an instance of socket
sock = socket.socket()
# make connection using the server and port
sock.connect((SERVER,PORT))
#  Send message for authentication to twitch channel
sock.send((	"PASS " + TOKEN + "\n" +
			"NICK " + NICKNAME + "\n" +
			"JOIN #" + CHANNEL + "\n").encode(ENCODING))


# configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler(f'./data/{CHANNEL}_chat.log', encoding=ENCODING)])

# define start time for timer
# startTime = dt.datetime.now()



def timer():
    ##  this function will be used to terminate the other functions based on the boolean...
    ## ... value of the global continueRunning variable

    global continueRunning


    # define start time for timer
    startTime = dt.datetime.now()

    while continueRunning:
        if dt.datetime.now() > (startTime + dt.timedelta(minutes=minutes)):
            print('timer hit in stopFuncs function')
            continueRunning =False
    print(continueRunning)



def stopButton():

    global continueRunning
    print('initiate stop button function')

    while continueRunning:
        print('before fedit')
        stopTwitch= fedit(data=[('Stop Twitchbot',True)],comment="<h3>Press ok to stop twitch bot</h3><br><h2>This dialouge box will reload until the program is terminated</h2>")[0]
        print(stopTwitch)
        print('after fedit')


        if stopTwitch:
            print('stop button')
            continueRunning = False






def sendMessage(so,outMessage):
    print('send message function hit')
    so.send("PRIVMSG #{} :{}\r\n".format(CHANNEL,outMessage).encode(ENCODING))


def output_test_function():

    global user
    global message
    global continueRunning

    while continueRunning:


        if message.lower() == 'test':
            # print('test message received')
            sendMessage(sock,'ECHO test')
            print('tBot Response send')

        #  if someone types in baby got back into the chat, it will respond with the lyrics
        if message.lower() == 'baby got back':

            with open('./data/babygotback.txt','r') as f:
                lyrics = f.read().split("\n")

                for lyric in lyrics:
                    sendMessage(sock,lyric)
                    time.sleep(random.choice([1,2,3]))

 
        message=''


        # if dt.datetime.now() > startTime + dt.timedelta(minutes=minutes):
        #     print('output test function ended due to timer')
        #     break




def readTwitch():

    global user
    global message
    global continueRunning

    def joinchat(): 
        loading = True
        while loading :

            print('waiting to receive initial chat')
            resp=sock.recv(2048).decode(ENCODING)

            # try:
            #     print('waiting to receive initial chat')
            #     resp=sock.recv(2048).decode(ENCODING)

            # except:
            #     print('error in join chat function')
            #     resp =''
            #     # continue
            
            logging.info(resp)

            print('------------')
            
            for line in resp.split('\n'):
                print(line)
                if("End of /NAMES list" in line):
                    loading = False
                    print(f'Joined stream of {CHANNEL}')
                    break

        logging.info('end of join chat function')

    def getuser(response):
        username = response.split('!')[0][1:]
        
        return username

    def getmsg(response):
        msg = response.split(f'PRIVMSG #{CHANNEL} :')[-1].replace('\r\n','')
        
        return msg

    joinchat()
    # sock.send("CAP REQ :twitch.tv/tags\r\n".encode())
    # https://dev.twitch.tv/docs/irc/tags
    # sock.send
    while continueRunning:

        # print('--------------------')
        # print('waiting for user message')
        # resp = sock.recv(2048).decode(ENCODING)
        try:
            resp = sock.recv(2048).decode(ENCODING)
            print('received respones from chat')
        except:
            continue
            # continue to while loop to retry the connection
            # resp =''
            # print('error getting resonse in readtwitch ')
            # break

        if "PING :tmi.twitch.tv" in resp:
            print('were playing ping pong')   
            logging.info('were playing ping pong')
            # send a pong
            sock.send("PONG :tmi.twitch.tv\r\n".encode(ENCODING))
        elif len(resp) > 0:
            logging.info(resp)
            if f'PRIVMSG #{CHANNEL} :' in resp:
                print('received message in chat from user')
                user = getuser(resp)
                message = getmsg(resp)
                print(f'{user}:{message}')


def main():
    if __name__=='__main__':


        t1 = threading.Thread(target=timer)

        t1.start()


        t2 = threading.Thread(target=stopButton)

        t2.start()
        

        # # t2 = threading.Thread(target = readTwitch,daemon=True)
        t3 = threading.Thread(target = readTwitch)
        t3.start()

        t4 = threading.Thread(target = output_test_function)
        t4. start()

        t1.join()
        t3.join()
        t4.join()
        t2.join()
        # t1.join()
        
        # sock.close()
        return

main()
print('end')
sock.close()