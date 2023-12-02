from socket import *
import threading

SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "Server Data"

def clientHandler(connSocket, addr):
    print(f"[CONNECTED] Connection with {addr} established.")
    connSocket.send("OK$Welcome to the File Exchange Server".encode(FORMAT))

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
