from socket import *
import threading
import sys
import pickle

"""
Derek Marshall - 170223090
Rebecca Knezy - 170767800
-----------------------------------------------------------------
server.py - Server that stores, sends and recieves notes
"""


"""
Board - Class - Used for the storing of notes, specifies colours, width and height of the board.

w - Width (int)
h - Height (int)
colours - List of colours (str[])
notes - List of posted notes (dictionaries)
"""

class Board:
    #Class to represent a bulletin board for notes

    def __init__(self, width, height, colours):
        self.w = width
        self.h = height
        self.colours = colours
        self.notes = [] #List of notes posted onto the board

    def _searchcoord (self, x, y):
        found = [] #List of indexes for found notes
        notfound = [] #List of indexes that dont contain coordinates
        for i in range(len(self.notes)):
            if self.notes[i]['coord'][0] <= x and self.notes[i]['coord'][1] <= y: #Note may be in coordinates
                if  self.notes[i]['coord'][0] + self.notes[i]['w'] - 1 >= x and self.notes[i]['coord'][1] + self.notes[i]['h'] - 1 >= y: #Coord contains note
                    found.append(i) #Append note to list
                else:
                    notfound.append(i)
            else:
                notfound.append(i)

        return found, notfound

    def getgen (self, coord = None, colour = None, contains = None):
        getNotes = self.notes.copy()
        if coord != None:
            removed = 0
            _, a = self._searchcoord(coord[0], coord[1])
            for i in a:
                getNotes.pop(i - removed)
                removed += 1

        if colour != None:
            i = 0
            while i < len(getNotes):
                if colour != getNotes[i]['col']:
                    getNotes.pop(i)
                    i -= 1 #Do this to prevent skipping item
                i += 1
        if contains != None:
            i = 0
            while i < len(getNotes):
                if contains not in getNotes[i]['m']:
                    getNotes.pop(i)
                    i -= 1
                i += 1
        return getNotes
            
    def getpin (self):
        pinned = []
        for i in self.notes:
            if i['s'] == 1: #Note is pinned
                pinned.append(i)
        if pinned == []:
            pinned = "ERROR"

        return pinned

    def pin (self, coord):
        flag = "ERROR"
        x = int(coord[0])
        y = int(coord[1])
        a, _ = self._searchcoord(x, y)
        for i in a:
            if self.notes[i]['s'] == 0:
                self.notes[i]['s'] = 1
                flag = "GOOD"
        return flag 
        

    def unpin (self, coord):
        flag = "ERROR"
        x = int(coord[0])
        y = int(coord[1])
        a = self._searchcoord(x, y)
        a, _ = self._searchcoord(x, y)
        for i in a:
            if self.notes[i]['s'] == 1:
                self.notes[i]['s'] = 0
                flag = "GOOD"
        return flag

    def clear (self):
        flag = "ERROR"
        i = 0
        while i < len(self.notes):
            if self.notes[i]['s'] == 0: #Note is not pinned
                self.notes.pop(i)
                i -= 1
                flag = "GOOD"
            i += 1
        return flag


"""
CThread - Class - A thread that will be created per user to allow multiple connections
"""

class CThread (threading.Thread):

    def __init__ (self, cAddr, cSock):
        threading.Thread.__init__(self)
        self.cSock = cSock
        print("New Connection Address: ", cAddr)

    def run (self):
        print("Connection from : ", cAddr)
        msg = ''
        for i in colours:
            msg += i
            msg += " "
        msg += str(argList[1])
        msg += " "
        msg += str(argList[2])
        self.cSock.send(msg.encode())
        msg = ''

        while True:
            data = self.cSock.recv(1024)
            msg = data.decode()

            if msg == 'DISCONNECT':
                break

            elif msg == 'CLEAR':
                flag = board.clear()
                self.cSock.send(flag.encode())

            else:
                msg = msg.split()
                if (msg[0] == 'POST'):
                    
                    message = "" 
                    for i in msg[6:-1]:
                        message += i
                        message += " "
                    message = message[0:-1] #Remove extra space from end of message
                    note = {'coord': [int(msg[1]), int(msg[2])], 'w': int(msg[3]), 'h': int(msg[4]), 'col': msg[5], 'm': message, 's': int(msg[-1])}
                    board.notes.append(note)
                    self.cSock.send("Posted".encode())

                elif (msg[0] == 'GET'):
                    if msg[1] == "contains=":
                        contains = "" 
                        for i in msg[2:]:
                            contains += i
                            contains +=" "
                        contains = contains[0:-1]
                        getNotes = board.getgen(contains=contains)
                        getNotes = pickle.dumps(getNotes)
                        self.cSock.send(getNotes)

                    elif msg[1] == "coord=":
                        coord = [int(msg[2]), int(msg[3])]
                        if len(msg) > 4 and msg[4] == "contains=":
                            contains = ""
                            for i in msg[4:]:
                                contains += i
                                contains+=" "
                            contains = contains[0:-1]
                            getNotes = board.getgen(coord=coord, contains=contains)
                            getNotes = pickle.dumps(getNotes)
                            self.cSock.send(getNotes)
                        else:
                            getNotes = board.getgen(coord=coord)
                            getNotes = pickle.dumps(getNotes)
                            self.cSock.send(getNotes)

                    elif msg[1] == "colour=":
                        colour = msg[2]
                        if len(msg) > 3 and msg[3] == "coord=":
                            coord = [int(msg[4]), int(msg[5])]
                            if len(msg) > 6 and msg[6] == "contains=":
                                contains = ""
                                for i in msg[7:]:
                                    contains += i
                                    contains +=" "
                                contains = contains[0:-1]
                                #all3
                                getNotes = board.getgen(colour=colour, coord=coord, contains=contains)
                                results = pickle.dumps(getNotes)
                                self.cSock.send(results)
                            else:
                                #col and coord
                                getNotes = board.getgen(colour=colour, coord=coord)
                                results = pickle.dumps(getNotes)
                                self.cSock.send(results)
                        else:
                            #just col
                            getNotes = board.getgen(colour=colour)
                            results = pickle.dumps(getNotes)
                            self.cSock.send(results)

                
                    elif msg[1] == "PINS":
                        pinned = board.getpin()
                        results = pickle.dumps(pinned)
                        self.cSock.send(results)

                    elif msg[1] == "ALL":
                        getNotes = board.getgen()
                        results = pickle.dumps(getNotes)
                        self.cSock.send(results)

                    #Error check and call board.get or board.getpin
                elif (msg[0] == 'PIN'):
                    coord = [msg[1], msg[2]]
                    flag = board.pin(coord)
                    self.cSock.send(flag.encode())
                    #error check coord and call board.pin
                elif (msg[0] == 'UNPIN'):
                    coord = [msg[1], msg[2]]
                    flag = board.unpin(coord)
                    self.cSock.send(flag.encode())
                    #error check coord and call board.unpin

        print ("Client at ", cAddr, " disconnected")

#serverPort, Width, Height, Colours

argList = sys.argv[1:]
colours = argList[3:] 
board = Board(argList[1], argList[2], colours) #init server board, global var in server

serverPort = int(argList[0])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))

print('Server is ready to recieve')

while True:
    serverSocket.listen(1)
    cSock, cAddr = serverSocket.accept()
    newThread = CThread(cAddr, cSock) #Adds new thread per user
    newThread.start()
