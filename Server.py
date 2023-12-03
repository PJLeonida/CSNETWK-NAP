from socket import *
import threading
import os

SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "Server Data"

def clientHandler(connSocket, addr):
    print(f"[CONNECTED] Connection with {addr} established.")
    connSocket.send("OK$Welcome to the File Exchange Server".encode(FORMAT))

    while True: 
        data = connSocket.recv(SIZE).decode(FORMAT)
        data = data.split(" ")
        command = data[0]

        if command == "register":
            response = "OK@"
            newUser = data[1] # Expects command to be /register <Alias>

            if newUser in users: # If user alias exists, send 'Exists', Otherwise send DNE
                response += "Exists"
                connSocket.send(response.encode(FORMAT))
                continue

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

            


def main():
    serverIP = 'localhost'
    serverPort = 6969
    bind = (serverIP, serverPort)

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(bind)
    serverSocket.listen(1)
    print("Server is listening...")
    while True:
        connSocket, addr = serverSocket.accept()
        thread = threading.Thread(target=clientHandler, args = (connSocket, addr))
        thread.start()

        
if __name__ == "__main__":
    main()