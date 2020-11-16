from socket import *
import sys
import pickle

"""
Derek Marshall - 170223090
Rebecca Knezy - 170767800
---------------------------------------------------------------------------------------
Client.py: Client to connect, disconnect, POST to, GET, PIN, UNPIN and CLEAR notes
from a server.
"""

connected = False

while True:
    while not connected:
        userIP = input("""
        Please select an action (1-7)

        1 - connect
        2 - disconnect
        3 - POST
        4 - GET
        5 - PIN
        6 - UNPIN
        7 - CLEAR
        """)

        if userIP == "1":
            clientSocket = socket(AF_INET, SOCK_STREAM)
            addr = input("Enter server address: ")
            while True:
                port = input("Enter server port: ")
                if not port.isdigit():
                    print("Invalid Port #")
                elif int(port) < 1024:
                    print("Cannot use privileged ports (ports less than 1024)")
                else:
                    port = int(port)
                    break
            try:
                clientSocket.connect((addr, port))
                msg = clientSocket.recv(1024) #List of colours
                msg = msg.decode()
                msg = msg.split()
                print(msg)
                colours = msg[0:-2]
                bWidth = int(msg[-2])
                bHeight = int(msg[-1])
                connected = True
            except:
                print("Invalid address or port")
        else:
            print("Must be connected to a server to perform that action")


    while connected:
        userIP = input("""
        Please select an action (1-7)

        1 - connect
        2 - disconnect
        3 - POST
        4 - GET
        5 - PIN
        6 - UNPIN
        7 - CLEAR
        """)

        if userIP == "1":
            print("Already connected to a server")

        elif userIP == "2":
            print("Disconnecting")
            clientSocket.send('DISCONNECT'.encode())
            connected = False
            clientSocket.close()

        elif userIP == "3":
            print("Colours: ", colours)
            print("Board Width", bWidth)
            print("Board Height", bHeight)

            while True:
                coord = input("Enter Coordinates x y: ")
                temp = coord.split()

                if len(temp) == 2:
                    if not temp[0].isdigit() or not temp[1].isdigit():
                        print("Invalid coordinates, coordinate values must be integers")
                    elif (int(temp[0]) > bWidth) or (int(temp[1]) > bHeight):
                        print("Invalid coordinates, out of board range")
                    else:
                        coord = coord.split()
                        break
                else:
                    if len(temp) == 1:
                        print("Invalid coordinates, must enter both x and y coordinate")
                    else:
                        print("Invalid coordinates, only 2 integer values allowed")

            while True:
                w = input("Enter note width: ")

                if w.isdigit():
                    if (int(w) + int(coord[0])) > bWidth:
                        print("Invalid Width, Out of board range")
                    elif (int(w) < 1):
                        print("Width must be greater than 0")
                    else:
                        break
                else:
                    print("Invalid Width, Please enter integer value")

            while True:
                h = input("Enter note height: ")

                if h.isdigit():
                    if (int(h) + int(coord[1])) > bHeight:
                        print("Invalid Height, Try again")
                    elif (int(h) < 1):
                        print("Height must be greater than 0")
                    else:
                        break
                else:
                    print("Invalid Height, Please enter integer value")

            while True:
                colour = input("Enter Colour of note: ")
                if colour not in colours:
                    print("Invalid colour, either not a colour or not in the list")
                else:
                    break

            m = input("Enter note message: ") #No input error checking needed
            
            while True:
                s = input("Enter not status (0 - Unpinned ; 1 - Pinned): ")
                if s == "0" or s == "1":
                    break
                else:
                    print("Invalid status, try again")

            clientSocket.send("POST {} {} {} {} {} {} {}".format(coord[0], coord[1], w, h, colour, m, s).encode())
            msg = clientSocket.recv(1024)
            msg = msg.decode()
            if msg == "ERROR":
                print("Error, note was not posted")
            else:
                print("Note was successfully posted")

        elif userIP == "4":
            c = input("""
            1 - Get General (Coordinate, Colour and/or Contains)
            2 - Get Pinned
            """)

            if c == "1":
                print("Colours: ", colours)
                print("Board Width", bWidth)
                print("Board Height", bHeight)

                while True:
                    colour = input("Enter Colour of note. Enter '0' to skip this input: ")
                    if colour != '0' and colour not in colours:
                        print("Invalid colour, try again")
                    else:
                        break

                while True:
                    coord = input("Enter Coordinates x y. Enter '0' to skip this input: ")
                    if coord != '0':
                        temp = coord.split()
                        if (len(temp) > 2 or len(temp) < 2):
                            print("Invalid cooridnates, must only enter 2 coordinate values")
                        elif not temp[0].isdigit or not temp[1].isdigit:
                            print("Invalid coordinates, must be integer values")
                        elif (int(temp[0]) > bWidth) or (int(temp[1]) > bHeight):
                            print("Invalid coordinates, out of board range")
                        else:
                            coord = coord.split()
                            break
                    else:
                        break

                contains = input("Enter substring contained within message. Enter '0' to skip this input: ") #Doesnt need IEC

                #Client Message based on 8 situations
                if coord == '0' and colour == '0' and contains == '0':
                    clientSocket.send('GET ALL'.encode())
                elif coord == '0' and colour == '0' and contains != '0':
                    clientSocket.send('GET contains= {}'.format(contains).encode())
                elif coord == '0' and colour != '0' and contains == '0':
                    clientSocket.send('GET colour= {}'.format(colour).encode())
                elif coord == '0' and colour != '0' and contains != '0':
                    clientSocket.send('GET colour= {} contains= {}'.format(colour, contains).encode())
                elif coord != '0' and colour == '0' and contains == '0':
                    clientSocket.send('GET coord= {} {}'.format(coord[0], coord[1]).encode())
                elif coord != '0' and colour == '0' and contains != '0':
                    clientSocket.send('GET coord= {} {} contains= {}'.format(coord[0], coord[1], contains).encode())
                elif coord != '0' and colour != '0' and contains == '0':
                    clientSocket.send('GET colour= {} coord= {} {}'.format(colour, coord[0], coord[1]).encode())
                else:
                    clientSocket.send('GET colour= {} coord= {} {} contains= {}'.format(colour, coord[0], coord[1], contains).encode())

                notes = clientSocket.recv(2048)
                notes = pickle.loads(notes)
                if notes == "ERROR":
                    print("GET ERROR, no Notes returned")
                else:
                    print("Successful Get! Printing Notes: ")
                    for i in notes:
                        print(i)


            elif c == "2":
                clientSocket.send('GET PINS'.encode())

                notes = clientSocket.recv(2048)
                notes = pickle.loads(notes)
                if notes == "ERROR":
                    print("GET ERROR, no Notes returned")
                else:
                    print("Successful Get! Printing Notes: ")
                    for i in notes:
                        print(i)

            else:
                print("Invalid Selection, Returning to main menu")

        elif userIP == "5":
            while True:
                coord = input("Enter Coordinates x y. Enter '0' to exit without pinning: ")
                if coord != '0':
                    temp = coord.split()
                    if (len(temp) > 2 or len(temp) < 2):
                        print("Invalid cooridnates, must only enter 2 coordinate values")
                    elif not temp[0].isdigit or not temp[1].isdigit:
                        print("Invalid coordinates, must be integer values")
                    elif (int(temp[0]) > bWidth) or (int(temp[1]) > bHeight):
                        print("Invalid coordinates, out of board range")
                    else:
                        coord = coord.split()
                        break
                else:
                    break

            if coord != '0':
                clientSocket.send('PIN {} {}'.format(coord[0], coord[1]).encode())
                msg = clientSocket.recv(1024)
                msg = msg.decode()
                if msg == "ERROR":
                    print("Error, No Notes Pinned")
                else:
                    print("Successful Pin!")

        elif userIP == "6":
            while True:
                coord = input("Enter Coordinates x y. Enter '0' to exit without unpinning: ")
                if coord != '0':
                    temp = coord.split()
                    if (len(temp) > 2 or len(temp) < 2):
                        print("Invalid cooridnates, must only enter 2 coordinate values")
                    elif not temp[0].isdigit or not temp[1].isdigit:
                        print("Invalid coordinates, must be integer values")
                    elif (int(temp[0]) > bWidth) or (int(temp[1]) > bHeight):
                        print("Invalid coordinates, out of board range")
                    else:
                        coord = coord.split()
                        break
                else:
                    break

            if coord != '0':
                clientSocket.send('UNPIN {} {}'.format(coord[0], coord[1]).encode())
                msg = clientSocket.recv(1024)
                msg = msg.decode()
                if msg == "ERROR":
                    print("Error, No Notes Unpinned")
                else:
                    print("Successful Unpin!")

        elif userIP == "7":
            clientSocket.send("CLEAR".encode())
            msg = clientSocket.recv(1024)
            msg = msg.decode()
            if msg == "ERROR":
                print("Error, No Notes Cleared")
            else:
                print("Successful Clear!")

        else:
            print("Invalid Selection, please select a new option")
