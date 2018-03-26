import socket
print("Hello")

def main():
    host = "10.0.0.93"
    port = 5000

    s = socket.socket()
    addr = None
    c = None
    try:
        s.bind((host, port))
        print("listening on port: " + str(port))
        s.listen(4)
        c, addr = s.accept()
        print("Connection to client: " + str(addr))

    except Exception as e:
        print("ERROR: " + str(e))
    
    while True:
        # Get data from client
        if c == None:
            print("SERVER: NoneType client. Exiting...")
            break

        data = c.recv(1024).decode('utf-8')
        if not data:
            break
        print("SERVER: message recieved: " + str(data))

        # Get input and send to client
        c.send(data.encode('utf-8'))
        if data == "q":
            print("SERVER: Shutting down...")
            break

if __name__ == "__main__":
    main()

