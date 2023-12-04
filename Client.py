import array
from importlib.metadata import files
from socket import *
import threading
import os
from urllib import request

import tkinter as tk
from tkinter import scrolledtext


connected = False # User joined server connection
clientSocket = socket(AF_INET, SOCK_STREAM)
userconn = False # User is registered

SIZE = 1024
FORMAT = "utf-8"
CLIENT_DATA_PATH = "Client Data"

commands = ["join <server_ip_add> <port>", "leave", "register <handle>", "store <filename>", "dir", "get <filename>"]
commanddesc = ["Connect to the server application", "Disconnect to the server application", "Register a unique handle or alias", "Send file to server", "Request directory file list from a server", "Fetch a file from a server"]

def send_command(event):
    global connected, clientSocket, userconn

    output_box.delete(1.0, tk.END) # Clears the message output field each time a command is executed
    
    data = command_entry.get()
    data = data.split(" ")
    command = data[0]
    commandistrue = False
    try:
        if command == "join":
            commandistrue = True
            # Sets the Server IP and Port to the user's inputs
            serverIP = data[1]
            serverPort = int(data[2])
            try: # Client tries to connect to the server's IP and port
                clientSocket.connect((serverIP, serverPort))
                data = clientSocket.recv(SIZE).decode(FORMAT)
                command, message = data.split("$")
                if command == "OK":
                    connected = True    
                    output_box.insert(tk.END,f"{message}") # Retrieves message from server verifying the connection
            except ConnectionRefusedError: # Displays error message if the server is not found
                output_box.insert(tk.END,"Error: Connection to the Server has failed! Please check IP Address and Port Number.")
        if command == "leave":
            commandistrue = True
            if not connected: # Displays error message if the Client is not connected to a Server
                output_box.insert(tk.END,"Error: Disconnection failed. Please connect to the server first.")
            else:
                output_box.insert(tk.END, "Disconnected From Server...")
                clientSocket.close() # Proceeds to Disconnect from the server
        if command == "get":
            commandistrue = True
            if not connected:  # Displays an error message if the Client is not connected to a Server
                output_box.insert(tk.END,"Error: Request failed. Please connect to the server first.")
            elif not userconn:
                output_box.insert(tk.END,"Error: Request failed. Please register a user before proceeding.")
            else:
                try:
                    filenameSeg = []
                    filenameStart = False
                    for name in data[1:]: # Allows spaces in filenames
                        if not filenameStart:
                            if name != "":
                                filenameStart = True
                                filenameSeg.append(name)
                        else:
                            filenameSeg.append(name)
                    filename = " ".join(filenameSeg)
                    request = "get@"+filename
                    clientSocket.send(request.encode(FORMAT))
                    if clientSocket.recv(SIZE).decode() == "OK":
                        if not os.path.exists(CLIENT_DATA_PATH):
                            os.makedirs(CLIENT_DATA_PATH)
                        clientSocket.send("OK".encode(FORMAT))
                        filepath = os.path.join(CLIENT_DATA_PATH, filename)
                        fileData = clientSocket.recv(SIZE)
                        with open(filepath, "wb") as receivedFile:
                            receivedFile.write(fileData)
                        output_box.insert(tk.END,f"File received from server: {filename}")
                    else:
                        output_box.insert(tk.END,"Error: File not found.")
                except Exception as e:
                    print("Error: " + e)
        if command == "dir":
            commandistrue = True
            clientSocket.send("dir".encode(FORMAT)) #Send Request of /dir
            fileString = clientSocket.recv(SIZE).decode(FORMAT) #receive the 1 aggregated string of all file names
            filenames = fileString.split("@") #split aggreagated string 
            for filename in filenames:
                output_box.insert(tk.END, filename) #print filenames
        if command == "?": # Displays all commands
            commandistrue = True
            for cmd, desc in zip(commands, commanddesc):
                output_box.insert(tk.END, f"{cmd} - {desc}\n")
        if command == "register":
            commandistrue = True
            if not connected: # Check if user is connected
                output_box.insert(tk.END,"Error: Registration failed. Please connect to the server first.")
                command_entry.delete(0, tk.END)
                return
            if len(data) != 2: # Check if user inputted proper parameters
                raise SyntaxError("Invalid Parameters")
            newUser = data[1] 
            request = command + "@" + newUser

            clientSocket.send(request.encode(FORMAT)) # Check if user handle is already used in server
            response = clientSocket.recv(SIZE).decode(FORMAT)
            response = response.split('@')

            if response[1] == "Exists":  # User exists in server
                output_box.insert(tk.END,"Error: Registration failed. Handle or alias already exists.")
                command_entry.delete(0, tk.END)
                return
            
            userconn = True
            output_box.insert(tk.END,"Hello, " + newUser + "!")

        if command == "store":
            commandistrue = True
            if not connected: # User has not joined
                output_box.insert(tk.END,"Error: Store failed. Please connect to the server.")
                command_entry.delete(0, tk.END)
                return
            elif not userconn: # User has not registered
                output_box.insert(tk.END,"Error: Store failed. Register a user before proceeding.")
                command_entry.delete(0, tk.END)
                return

            if len(data) != 2: # Check if user inputted proper parameters
                raise SyntaxError("Invalid Parameters")
            
            try: # Check if file Exists. If not, send error
                filename = data[1]
                filePath = os.path.join(CLIENT_DATA_PATH, filename)
                request = command + "@" + filename
                clientSocket.send(request.encode(FORMAT))

                with open(filePath, "rb") as file: # Open and Read file
                    fileData = file.read() 
                clientSocket.sendall(fileData) # Send file to server

                response = clientSocket.recv(SIZE).decode(FORMAT) # Get response
                response = response.split('@')

                if response[0] != "OK": # Server error
                    output_box.insert(tk.END,"Error: Failed to send to server.")
                    command_entry.delete(0, tk.END)
                    return

                output_box.insert(tk.END,response[1])
            except FileNotFoundError: 
                output_box.insert(tk.END,"Error: File does not exists in Client Data folder")
                command_entry.delete(0, tk.END)
                return
        if not commandistrue:
            output_box.insert(tk.END,"Error: Command not found.")
    except Exception as e:
        output_box.insert(tk.END,"Error: Command parameters do not match or is not allowed.")
        print(f"Error: {e}")
    
    command_entry.delete(0, tk.END)



root = tk.Tk()
root.title("File Exchange Application")
root.geometry("750x500")

command_frame = tk.Frame(root)
command_label = tk.Label(command_frame, text="/")
command_entry = tk.Entry(command_frame, width=50)
command_entry.bind("<Return>", send_command)

command_label.pack(side=tk.LEFT)
command_entry.pack(side=tk.LEFT)
command_frame.pack(pady=10)

tip_label = tk.Label(root, text="Tip: Enter the command /? for the list of commands!")
tip_label.pack(pady=1)

output_frame = tk.Frame(root)
output_label = tk.Label(output_frame, text="Message Box:")
output_box = scrolledtext.ScrolledText(output_frame, width=90, height=15)

output_label.pack()
output_box.pack(padx=10)
output_frame.pack(pady=10)



root.mainloop()

clientSocket.close()
