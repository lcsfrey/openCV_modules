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
        image_byte_size = b''
        current = self.sock.recv(1)
        print(current)
        if current == b'X': 
            return None

        while current != b'|':
            image_byte_size += current
            current = self.sock.recv(1)
            
            

        image_byte_size = int(image_byte_size)

        data = b''
        packet_size = 2048
        while len(data) < image_byte_size:
            packet_size = min(2048, image_byte_size - len(data))
            data += self.sock.recv(packet_size)

        return cv2.imdecode(pickle.loads(data), cv2.IMREAD_COLOR)


# Open a single frame to send
# TODO: Add text to
def main():
    print("TCP client Running")
    image = None
    try:
        connection = TCPClientProtocol()
        connection.connect()
        
    except Exception as e:
        print("ERROR: " + str(e))
        return

    while True:
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
        image = connection.recv_img()

        if image is None:
            break
        cv2.imshow("CLIENT: Frame received", image)

if __name__ == "__main__":
    main()
