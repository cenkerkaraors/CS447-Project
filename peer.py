import socket
import os, time
from os import listdir
from os.path import isfile, join
import pickle
#/Users/denis/Documents/Server

# Common
def analyzeContent(directory): # Takes a directory and returns a list of contents
    contentList = os.listdir(directory)
    contentTupleList = []
    for x in contentList :
        #tup = (x, time.ctime(os.path.getmtime(directory + "/" + x)))
        tup = (x, os.path.getmtime(directory + "/" + x))
        contentTupleList.append(tup)
    return contentTupleList

def sendList(list_input,conn): # Sends List takes list
    data = pickle.dumps(list_input)
    conn.send(data)

def includes(target,list_input) : # returns 1 if exists otherwise -1
    for x in list_input :
        if(target[0] == x[0]) : return 1
    return -1

def ifUpdated(target,list_input) : # returns 1 if file is updated version otherwise -1
    for x in range(0,len(list_input)-1) :
        if(target[0] == list_input[x][0]) :
            if(target[1] > list_input[x][1]) : return 1
    return 0

def compareFiles(list_self,list_peer) : # Makes a list of missing and updated files
    outgoing = []
    for x in list_self : # Handles missing files
        if(includes(x,list_peer) == -1) : outgoing.append(x)
    for x in outgoing :
        list_self.remove(x)
    for x in list_self :
        if(ifUpdated(x,list_peer)) : outgoing.append(x)
        
    print("Outgoing: ")
    print(outgoing)
    return outgoing
# Server Specific
def sendFile_Server(directory,file_name,server_socket): # Send Files takes file_name and connection
    control = 1
    while control :
        conn, address = server_socket.accept()
        print("Connected to Client")

        f = open(directory + "/" + file_name,'rb')
        data = f.read(1024)
        while(data):
            conn.send(data)
            data = f.read(1024)
        f.close()
        conn.close()
        control = 0
    print("File Sent: ", file_name)

def recvFile_Server(directory,file_name,server_socket) :
    control = 1
    while control :
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
#/home/cenkerkaraors/Desktop/CS447Test/Client
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

def recvFile_Client(directory, file_name, ip) :
    temp_socket = socket.socket()
    port = 5000
    temp_socket.connect((ip,port))
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

def sendFile_Client(directory,file_name, ip) :
    temp_socket = socket.socket()
    port = 5000
    temp_socket.connect((ip,port))
    
    f = open(directory + "/" + file_name,'rb')
    data = f.read(1024)
    while(data):
        temp_socket.send(data)
        data = f.read(1024)
    f.close()
    temp_socket.close()
    print("File Sent: ", file_name)

def sync_Client(client_folder,client_socket,ip): # Syncs a folder takes folder and connection
    folder_request = input("Enter Request: ")
    client_socket.send(folder_request.encode())

    response = client_socket.recv(1024)
    print("Server Response: ",response.decode())
    

    client_files = analyzeContent(client_folder)
    sendList(client_files,client_socket)

    server_data = client_socket.recv(1024)
    server_files = pickle.loads(server_data)


    print("Client Files: :",client_files)
    print("Server Files:",server_files)

    outgoing = compareFiles(client_files,server_files)

    # At this point we have all needed informatio
    message = "ok"
    response = client_socket.recv(1024).decode()
    while(response == "1") :
        message = "ok" 
        client_socket.send(message.encode()) # send ok
        filename = client_socket.recv(1024).decode()
        recvFile_Client(client_folder, filename, ip) # received file
        
        
        message = ""

        response = client_socket.recv(1024).decode() # continue or not

    # Client Sends
    print("Sending Files: ")
    message = "1"
    client_socket.send(message.encode())
    for x in range(len(outgoing)) :
        if(client_socket.recv(1024).decode() == "ok")  :
            filename = outgoing[x][0]
            client_socket.send(filename.encode())
            sendFile_Client(client_folder, filename, ip)

            if( x != len(outgoing)-1) :
                message = "1"
                client_socket.send(message.encode())
            else :
                message = "0"
                client_socket.send(message.encode()) # Done





def init_Server() :
    server_socket = socket.socket()
    ip =  '0.0.0.0'
    port = 5000

    server_socket.bind((ip,port))

    server_socket.listen(10)

    print("Server Started")
    print("Waiting Connection...")

    control = 1
    while control :
        conn, address = server_socket.accept()
        print("Connected to Client")

        request = conn.recv(1024).decode() # Client Request
        print("Client Request: ",request)


        message = "Your Request " + request
        conn.send(message.encode())

        
        sync_Server(request,conn,server_socket)
        
        conn.close
        control = 0

    server_socket.close()
    print("Closed")

def init_Client() :
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
    ip = '192.168.1.20' # home ipv4

    ip = '192.168.1.25'
    print("Info",ip)
    print("Host: ", ip)
    port = 5000


    print("Client Started")
    client_socket.connect((ip,port))
    print("Connected to Server")

    sync_Client('/home/cenkerkaraors/Desktop/CS447Test/Client',client_socket,ip)


    client_socket.close()
    print("Closed")# done


# Main
init_Client()