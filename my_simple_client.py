import socket

def Main():
    host = "10.0.0.93"
    port = 5000

    s = socket.socket()
    print("Attempting to connect to address: " + host + " at port " + str(port))
    s.connect((host, port))

    print("Enter a message")
    message = input("->")
    while message != "q":
        s.send(message.encode('utf-8'))
        data = s.recv(1024).decode('utf-8')
        print("Received from server: " + str(data))
        message = input("->")
    s.close()

if __name__ == "__main__":
    Main()