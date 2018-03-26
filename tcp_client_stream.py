import cv2
import MyCamera
import time
import socket
import pickle

class TCPClientProtocol:
    def __init__(self, host=None, port=None):

        if host is None:
            self.host = 'localhost'
        else:
            self.host = host

        if port is None:
            self.port = 5000
        else:
            self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

       
    '''
    Used to initialize socket
    '''
    def connect(self):
        print("CLIENT: Establishing connection...")
        self.sock.connect((self.host, self.port))
        print("CLIENT: Connection established...")


    '''
    receive image from server
    '''
    def recv_img(self):
        data = b''
        packet_size = 1024
        image_byte_size = 640 * 480 * 3
        while image_byte_size > 0:
            if image_byte_size >= packet_size:
                data += self.sock.recv(packet_size)
            else:
                data += self.sock.recv(image_byte_size)
            image_byte_size -= packet_size
        return cv2.imdecode(pickle.loads(data), cv2.IMREAD_COLOR)


# Open a single frame to send
# TODO: Add text to
def main():
    print("TCP client Running")
    image = None
    try:
        connection = TCPClientProtocol()
        connection.connect()
        image = connection.recv_img()

    except Exception as e:
        print("ERROR: " + str(e))
        return

    while True:
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
        
        cv2.imshow("CLIENT: Frame received", image)

if __name__ == "__main__":
    main()
