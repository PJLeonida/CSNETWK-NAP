from socket import *
import threading
import os
import datetime 
import pickle

SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "Server Data"

def clientHandler(connSocket, addr, users):
    print(f"[CONNECTED] Connection with {addr} established.")
    connSocket.send("OK$Welcome to the File Exchange Server".encode(FORMAT))
    reg_user = ""

    while True: 
        data = connSocket.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        command = data[0]

        if command == "register":
            response = "OK@"
            newUser = data[1] # Expects command to be /register <Alias>

            if newUser in users: # If user alias exists, send 'Exists', Otherwise send DNE
                response += "Exists"
                connSocket.send(response.encode(FORMAT))
                continue
            
            reg_user = newUser
            users.append(newUser) # Append user to list of registered users
            response += "DNE"
            connSocket.send(response.encode(FORMAT))

        if command == "dir":
            filenames = os.listdir("Server Data")
            fileString = ""
            for filename in filenames:
                print(filename)
                fileString += filename + "@"
            connSocket.send(fileString.encode(FORMAT))
            print(fileString)


        if command == "get":
            filename = data[1]
            filePath = os.path.join(SERVER_DATA_PATH, filename)
            try:
                if os.path.exists(filePath):
                    connSocket.send("OK".encode(FORMAT))
                    print(f"[GET REQUEST] {reg_user} +  is requesting to get {filename}")
                else:
                    connSocket.send("FILE NOT FOUND.".encode(FORMAT))
                if connSocket.recv(1024).decode() == "OK":
                    with open(filePath, "rb") as file:
                        fileData = file.read()
                        connSocket.sendall(fileData)
                    timedate = datetime.datetime.now()
                    date = timedate.strftime("%x")
                    time = timedate.strftime("%X")
                    print(reg_user + " (" + date + " " + time + "): Received " + filename)
            except Exception as e:
                connSocket.send("ERROR".encode(FORMAT))
                print(f"Error: {e}")    


        if command == "store":
            filename = data[1]
            if not os.path.exists(SERVER_DATA_PATH):
                os.makedirs(SERVER_DATA_PATH)

            try:
                filePath = os.path.join(SERVER_DATA_PATH,filename)
                with open(filePath, "wb") as file: # Write to file
                    request_file = connSocket.recv(1024)
                    file_data = request_file.decode(FORMAT)
                    if not request_file.decode(FORMAT) == "FILE NOT FOUND":
                        file.write(request_file)
                        error = False
                    else:
                        print(f"Error: file not found.")
                        error = True

                if error: # If error send Error response status
                    response = "ERROR@File not found"
                    connSocket.send(response.encode(FORMAT))
                    continue
                
                # If success send success reponse to client
                timedate = datetime.datetime.now()
                date = timedate.strftime("%x")
                time = timedate.strftime("%X")
                response = "OK@" + reg_user + " (" + date + " " + time + "): Uploaded " + filename
                print(reg_user + " (" + date + " " + time + "): Uploaded " + filename)
                connSocket.send(response.encode(FORMAT))
            except Exception as e:
                print(f"Error: ", e)


def main():
    serverIP = 'localhost'
    serverPort = 6969
    bind = (serverIP, serverPort)
    users = []

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(bind)
    serverSocket.listen(1)
    print("Server is listening...")
    while True:
        connSocket, addr = serverSocket.accept()
        thread = threading.Thread(target=clientHandler, args = (connSocket, addr, users))
        thread.start()

        
if __name__ == "__main__":
    main()
