import array
from importlib.metadata import files
from socket import *
import threading
import os
from urllib import request

SIZE = 1024
FORMAT = "utf-8"
CLIENT_DATA_PATH = "Client Data"

commands = ["join <server_ip_add> <port>", "leave", "register <handle>", "store <filename>", "dir", "get <filename>"]
commanddesc = ["Connect to the server application", "Disconnect to the server application", "Register a unique handle or alias", "Send file to server", "Request directory file list from a server", "Fetch a file from a server"]
def main():
    connected = False # User joined server connection
    clientSocket = socket(AF_INET, SOCK_STREAM)
    userconn = False # User is registered

    while True:
        data = input("/ ")
        data = data.split(" ")
        command = data[0]
        try:
            if command == "join":
                # Sets the Server IP and Port to the user's inputs
                serverIP = data[1]
                serverPort = int(data[2])
                try: # Client tries to connect to the server's IP and port
                    clientSocket.connect((serverIP, serverPort))
                    data = clientSocket.recv(SIZE).decode(FORMAT)
                    command, message = data.split("$")
                    if command == "OK":
                        connected = True    
                        print(f"{message}") # Retrieves message from server verifying the connection
                except ConnectionRefusedError: # Displays error message if the server is not found
                    print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
            elif command == "leave":
                if not connected: # Displays error message if the Client is not connected to a Server
                    print("Error: Disconnection failed. Please connect to the server first.")
                else:
                    break # Proceeds to Disconnect from the server
            elif command == "dir":
                clientSocket.send("dir".encode(FORMAT)) #Send Request of /dir
                fileString = clientSocket.recv(SIZE).decode(FORMAT) #receive the 1 aggregated string of all file names
                filenames = fileString.split("@") #split aggreagated string 
                for filename in filenames:
                    print(filename) #print filenames
            elif command == "?": # Displays all commands
                print("-COMMANDS-")
                for cmd, desc in zip(commands, commanddesc):
                    print(cmd + " - " + desc)
                print('\n')
            elif command == "register":
                if not connected: # Check if user is connected
                    print("Error: Registration failed. Please connect to the server first.")
                    continue
                if len(data) != 2: # Check if user inputted proper parameters
                    raise SyntaxError("Invalid Parameters")
                newUser = data[1] 
                request = command + " " + newUser

                clientSocket.send(request.encode(FORMAT)) # Check if user handle is already used in server
                response = clientSocket.recv(SIZE).decode(FORMAT)
                response = response.split('@')

                if response[1] == "Exists":  # User exists in server
                    print("Error: Registration failed. Handle or alias already exists.")
                    continue
                
                userconn = True
                print("Hello, " + newUser + "!")

            elif command == "store":
                if not connected: # User has not joined
                    print("Error: Store failed. Please connect to the server.")
                    continue
                elif not userconn: # User has not registered
                    print("Error: Store failed. Register a user before proceeding.")
                    continue

                if len(data) != 2: # Check if user inputted proper parameters
                    raise SyntaxError("Invalid Parameters")
                
                try: # Check if file Exists. If not, send error
                    filename = data[1]
                    filePath = os.path.join(CLIENT_DATA_PATH, filename)
                    request = command + " " + filename
                    clientSocket.send(request.encode(FORMAT))

                    with open(filePath, "rb") as file: # Open and Read file
                        fileData = file.read() 
                    clientSocket.sendall(fileData) # Send file to server

                    response = clientSocket.recv(SIZE).decode(FORMAT) # Get response
                    response = response.split('@')

                    if response[0] != "OK": # Server error
                        print("Error: Failed to send to server.")
                        continue

                    print(response[1])
                except FileNotFoundError: 
                    print("Error: File does not exists in Client Data folder")
                    continue
            else:
                print("Error: Command not found.")
        except Exception:
            print("Error: Command parameters do not match or is not allowed.")
    clientSocket.close()
    print("Disconnected From Server...")




if __name__ == "__main__":
    main()