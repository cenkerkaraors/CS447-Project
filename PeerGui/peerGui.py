from tkinter import *
from functools import partial
from tkinter import messagebox
import threading
from threading import Thread
# Peer imports
import socket
import os, time
from os import listdir
from os.path import isfile, join
import pickle
import sys


directory_List = []
# Common
def analyzeContent(directory):  # Takes a directory and returns a list of contents
    contentList = os.listdir(directory)
    contentTupleList = []
    for x in contentList:
        tup = (x, os.path.getmtime(directory + "/" + x))
        contentTupleList.append(tup)
    return contentTupleList


def sendList(list_input, conn):  # Sends List takes list
    data = pickle.dumps(list_input)
    conn.send(data)


def includes(target, list_input):  # returns 1 if exists otherwise -1
    for x in list_input:
        if (target[0] == x[0]): return 1
    return -1


def ifUpdated(target, list_input):  # returns 1 if file is updated version otherwise -1
    for x in range(0, len(list_input) - 1):
        if (target[0] == list_input[x][0]):
            if (target[1] > list_input[x][1]): return 1
    return 0


def compareFiles(list_self, list_peer):  # Makes a list of missing and updated files
    outgoing = []
    for x in list_self:  # Handles missing files
        if (includes(x, list_peer) == -1): outgoing.append(x)
    for x in outgoing:
        list_self.remove(x)
    for x in list_self:
        if (ifUpdated(x, list_peer)): outgoing.append(x)

    print("Outgoing: ")
    print(outgoing)
    return outgoing


# Server Specific
def sendFile_Server(directory, file_name, server_socket):  # Send Files takes file_name and connection
    control = 1
    while control:
        conn, address = server_socket.accept()
        print("Connected to Client")

        f = open(directory + "/" + file_name, 'rb')
        data = f.read(1024)
        while (data):
            conn.send(data)
            data = f.read(1024)
        f.close()
        conn.close()
        control = 0
    print("File Sent: ", file_name)


def recvFile_Server(directory, file_name, server_socket):
    control = 1
    while control:
        conn, address = server_socket.accept()
        print("Connected to Client")

        with open(directory + "/" + file_name, 'wb') as f:
            while True:
                print('receiving data...')
                data = conn.recv(1024)
                if not data:
                    break
                f.write(data)
            f.close()

        conn.close()
        control = 0
    print("File Received: ", file_name)


# /home/cenkerkaraors/Desktop/CS447Test/Client
def sync_Server(folder, conn, server_socket):  # Syncs a folder takes folder and connection
    server_files = analyzeContent(folder)
    sendList(server_files, conn)

    client_data = conn.recv(1024)
    client_files = pickle.loads(client_data)

    print("Server Files: :", server_files)
    print("Client Files:", client_files)

    outgoing = compareFiles(server_files, client_files)
    print("Sending Files: ")
    # At this point we have all needed information
    message = "1"
    conn.send(message.encode())  # I have files to send

    for x in range(len(outgoing)):
        if (conn.recv(1024).decode() == "ok"):
            filename = outgoing[x][0]
            conn.send(filename.encode())
            sendFile_Server(folder, filename, server_socket)

            if (x != len(outgoing) - 1):
                message = "1"
                conn.send(message.encode())  # I have some file
            else:
                message = "0"
                conn.send(message.encode())

    print("Server Receiving: ")
    message = "ok"
    response = conn.recv(1024).decode()
    while (response == "1"):
        message = "ok"
        conn.send(message.encode())
        filename = conn.recv(1024).decode()
        recvFile_Server(folder, filename, server_socket)
        message = ""
        response = conn.recv(1024).decode()


# Client Specific

def recvFile_Client(directory, file_name, ip):
    temp_socket = socket.socket()
    port = 5000
    temp_socket.connect((ip, port))
    with open(directory + "/" + file_name, 'wb') as f:
        while True:
            print('receiving data...')
            data = temp_socket.recv(1024)
            if not data:
                break
            f.write(data)
        f.close()
    print('File Received: ', file_name)
    temp_socket.close()
    print('connection closed')


def sendFile_Client(directory, file_name, ip):
    temp_socket = socket.socket()
    port = 5000
    temp_socket.connect((ip, port))

    f = open(directory + "/" + file_name, 'rb')
    data = f.read(1024)
    while (data):
        temp_socket.send(data)
        data = f.read(1024)
    f.close()
    temp_socket.close()
    print("File Sent: ", file_name)


def sync_Client(client_folder, client_socket, ip):  # Syncs a folder takes folder and connection
    folder_request = directory_List[0][1]
    client_socket.send(folder_request.encode())

    response = client_socket.recv(1024)
    print("Server Response: ", response.decode())

    client_files = analyzeContent(client_folder)
    sendList(client_files, client_socket)

    server_data = client_socket.recv(1024)
    server_files = pickle.loads(server_data)

    print("Client Files: :", client_files)
    print("Server Files:", server_files)

    outgoing = compareFiles(client_files, server_files)

    # At this point we have all needed informatio
    message = "ok"
    response = client_socket.recv(1024).decode()
    while (response == "1"):
        message = "ok"
        client_socket.send(message.encode())  # send ok
        filename = client_socket.recv(1024).decode()
        recvFile_Client(client_folder, filename, ip)  # received file

        message = ""

        response = client_socket.recv(1024).decode()  # continue or not

    # Client Sends
    print("Sending Files: ")
    message = "1"
    client_socket.send(message.encode())
    for x in range(len(outgoing)):
        if (client_socket.recv(1024).decode() == "ok"):
            filename = outgoing[x][0]
            client_socket.send(filename.encode())
            sendFile_Client(client_folder, filename, ip)

            if (x != len(outgoing) - 1):
                message = "1"
                client_socket.send(message.encode())
            else:
                message = "0"
                client_socket.send(message.encode())  # Done


def init_Server():
    server_socket = socket.socket()
    ip = '0.0.0.0'
    port = 5000

    server_socket.bind((ip, port))

    server_socket.listen(10)

    print("Server Started")
    print("Waiting Connection...")


    control = 1
    while control:
        conn, address = server_socket.accept()
        print("Connected to Client")

        request = conn.recv(1024).decode()  # Client Request
        print("Client Request: ", request)

        message = "Your Request " + request
        conn.send(message.encode())

        sync_Server(request, conn, server_socket)

        conn.close
        control = 0

    server_socket.close()
    print("Closed")


def init_Client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    ip = ''
    print("Info", ip)
    print("Host: ", ip)
    port = 5000

    print("Client Started")
    client_socket.connect((ip, port))
    print("Connected to Server")
    # /home/cenkerkaraors/Desktop/CS447Test/Client
    sync_Client(directory_List[0][0], client_socket, ip)

    client_socket.close()
    print("Closed")  # done


# GUI

# Add Directories Page
def add_CallBack():
    directory_Page = Toplevel()
    directory_Page.title("Add Directory")
    directory_Page.geometry('400x220+400+300')

    src_label = Label(directory_Page, text="Enter Source Location here: ")
    src_label.grid(row=1, column=1)
    src_entry = Entry(directory_Page, bd=2)
    src_entry.grid(row=1, column=2)

    dest_label = Label(directory_Page, text="Enter Destination Location here: ")
    dest_label.grid(row=2, column=1)

    dest_entry = Entry(directory_Page, bd=2)
    dest_entry.grid(row=2, column=2)

    dir_add = Button(directory_Page, text="Add", fg="black", command=partial(dir_CallBack, src_entry, dest_entry))
    dir_add.grid(row=3, column=2)

    exit_button = Button(directory_Page, text="Exit", fg="black", command=partial(exit_CallBack, directory_Page))
    exit_button.grid(row=4, column=2)
    
    directory_Page.mainloop()


def sync_CallBack():
    init_Client()

    myStr = ""
    for x in directory_List:
        myStr = myStr + "From: " + x[0] + " To: " + x[1] + "\n"

    messagebox.showinfo(message="Sync Complete: \n" + myStr)


def exit_CallBack(page):
    page.withdraw()

def close_CallBack(page):
    page.withdraw()
    
def clean_CallBack(parent) :
    directory_List.clear()
    saveDirectories()
    showDirs(parent) 

def dir_CallBack(src_entry, dest_entry):
    tup = (src_entry.get(), dest_entry.get())
    directory_List.append(tup)
    messagebox.showinfo(message="Directory Added: " + tup[0] + " -> " + tup[1])


def showDirs(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    for x in range(len(directory_List)):
        str = directory_List[x][0] + '   --->   ' + directory_List[x][1]
        label = Label(parent, text=str, bg="white")
        label.pack()

    saveDirectories()

def saveDirectories() :
    f = open('save.txt', 'w')
    f.truncate(0)

    for x in directory_List :
        str = x[0] + " " + x[1] + "\n"
        f.write(str)

def loadDirectories() :
    f = open('save.txt', 'r')
    lines = f.readlines()

    for x in lines :
        if (x != "") :
            temp = x.split()
            if(len(temp) == 2) :
                tup = (temp[0], temp[1])
                directory_List.append(tup)


def init_gui():

    # Intial Functions

    loadDirectories()

    # Main Page

    root = Tk()
    root.title("S-Play")
    root.geometry("600x600")

    # Frames
    top_frame = Frame(root, bg='#282828', bd=2)
    top_frame.pack(side=TOP, fill=X)

    left_frame = Canvas(root, height=500, width=600, bg="#282828")
    left_frame.pack()

    center_frame = Frame(left_frame, bg="white")
    center_frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

    right_frame = Frame(root)
    right_frame.pack(side=RIGHT)

    # Buttons

    img_add = PhotoImage(file='addnew.gif')
    add_Button = Button(top_frame, text="Add", command=add_CallBack, compound=TOP, image=img_add)
    add_Button.pack(side=LEFT)

    img_sync = PhotoImage(file='syncbutton.gif')
    sync_Button = Button(top_frame, text="Sync", command=sync_CallBack, compound=TOP, image=img_sync)
    sync_Button.pack(side=RIGHT)

    exit_Button = Button(top_frame, text="Exit", command=partial(close_CallBack,root), compound=TOP)
    exit_Button.pack(side=RIGHT)

    img_refresh = PhotoImage(file='refresh.gif')
    refresh_Button = Button(top_frame, text="Refresh", command=partial(showDirs, center_frame), compound=TOP, image=img_refresh)
    refresh_Button.pack()
    
    clean_Button =  Button(top_frame, text="Clean", command=partial(clean_CallBack,center_frame), compound=TOP)
    clean_Button.pack(side=RIGHT)

    #End

    showDirs(center_frame)
    root.resizable(True, True)
    root.mainloop()


class part1(Thread):
    def run(self):
        init_gui()


class part2(Thread):
    def run(self):
        init_Server()


t2 = part2()
t2.start()

init_gui()


