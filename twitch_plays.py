import socket
import logging
import datetime as dt
import threading
import time
from ahk import AHK
import random
from config import TOKEN, HOT_KEY_PATH, CHANNEL, NICKNAME

from formlayout import fedit


# # I think I might want to use queues instead of modifying global variables
### https://stackoverflow.com/questions/19790570/using-a-global-variable-with-a-thread
# from queue import Queue


# global variables
message = ""
user = ""
continueRunning = True


# I might want to move this to the config file
SERVER = 'irc.chat.twitch.tv'
PORT = 6667
ENCODING = 'utf-8'


# initialize hotkey 
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



# # set the number of minutes for the timeer
# minutes = 3

# # define start time for timer
# # startTime = dt.datetime.now()

# def timer():
#     ##  this function will be used to terminate the other functions based on the boolean...
#     ## ... value of the global continueRunning variable

#     global continueRunning

#     # define start time for timer
#     startTime = dt.datetime.now()

#     while continueRunning:
#         if dt.datetime.now() > (startTime + dt.timedelta(minutes=minutes)):
#             print('timer hit in stopFuncs function')
#             continueRunning =False
#     print(f'timer while left{continueRunning}')



def gui():

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
    print('gui while left')


# #### untested version of gui function with multiple options
# def gui():

#     global continueRunning
#     print('initiate stop button function')

#     while continueRunning:
#         print('before fedit')

#         data =[('tuple *', (0, 'Send Message', 'Stop Program'))]
#         stopTwitch= fedit(data=data,comment="<h3>Press ok to stop twitch bot</h3><br><h2>This dialouge box will reload until the program is terminated</h2>")[0]
#         print(stopTwitch)
#         print('after fedit')


#         if stopTwitch[0]==2:
#             print('stop button')
#             continueRunning = False
        
#         if stopTwitch[0]==1:
#             print('gui message send')
#             sendMessage(sock,'test message sent from py gui')



#  sends message to twitch channel with a socket and outmessage
def sendMessage(so,outMessage):
    print('send message function hit')
    so.send("PRIVMSG #{} :{}\r\n".format(CHANNEL,outMessage).encode(ENCODING))

#  this is a test function that listens for messages from the chat and responds
def output_test_function():

    global user
    global message
    global continueRunning

    while continueRunning:


        if message.lower() == 'test':
            # print('test message received')
            sendMessage(sock,'ECHO test')
            print('tBot Response send')
            message=''



        #  if someone types in baby got back into the chat, it will respond with the lyrics
        if message.lower() == 'baby got back':

            message=''

            with open('./data/babygotback.txt','r') as f:
                lyrics = f.read().split("\n")

                for lyric in lyrics:
                    sendMessage(sock,lyric)
                    time.sleep(random.choice([1,2,3]))

    print('output while left')


def gamecontrol():

    global message
    global continueRunning

    while continueRunning:

        if "up" == message.lower():
            ahk.key_press('up')
            message = ""

        if "down" == message.lower():
            ahk.key_press('down')
            message = ""

        if "left" == message.lower():
            ahk.key_press('left')
            message = ""

        if "right" == message.lower():
            ahk.key_press('right')
            message = ""

        if "a" == message.lower():
            ahk.key_press('z')
            message = ""

        if "b" == message.lower():
            ahk.key_press('x')
            message = ""

        if "lb" == message.lower():
            ahk.key_press('a')
            message = ""

        if "rb" == message.lower():
            ahk.key_press('s')
            message = ""

        if "select" == message.lower():
            ahk.key_press('d')
            message = ""

        if "start" == message.lower():
            ahk.key_press('enter')
            message = ""
    print('game controls left')





def readTwitch():

    global user
    global message
    global continueRunning

    def joinchat(): 
        loading = True
        while loading :

            print('waiting to receive initial chat')
            resp=sock.recv(2048).decode(ENCODING)


            logging.info(resp)

            print('------------')
            
            for line in resp.split('\n'):
                print(line)
                if("End of /NAMES list" in line):
                    loading = False
                    print(f'Joined stream of {CHANNEL}')
                    break
        print('end of join chat while loop')
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

        #  not sure if I should keepe this try block
        try:
            resp = sock.recv(2048).decode(ENCODING)
            print('received respones from chat')
        except:
            continue


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
    print('left readtwitch while loop')

def main():
    if __name__=='__main__':


        # tTimer = threading.Thread(target=timer)
        tGui = threading.Thread(target=gui)
        tReadTwitch = threading.Thread(target = readTwitch)
        tOutput = threading.Thread(target = output_test_function)
        tGame = threading.Thread(target=gamecontrol)




        # tTimer.start()
        tGui.start()
        tReadTwitch.start()
        # tOutput. start()
        tGame.start()





        # tTimer.join()
        tGui.join()
        tOutput.join()
        tReadTwitch.join()
        tGame.join()
         
        
        sock.close()
        return

main()
print('end')
# sock.close()