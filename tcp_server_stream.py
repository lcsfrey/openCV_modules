import cv2
from MyCamera import MyCamera
import time
import socket
import pickle

class TCPServerProtocol:
    def __init__(self, host=None, port=None):
        self.client = None
        self.client_address = None

        if host is None:
            self.host = 'localhost'
        else:
            self.host = host

        if port is None:
            self.port = 5000
        else:
            self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server socket created")
    
    def listen(self):
        self.sock.bind((self.host, self.port))
        print("listening on port:", self.port)
        self.sock.listen(1)

    def accept(self):
        print("Waiting for connection...")
        self.client, self.client_address = self.sock.accept()    
        print("Connection acquired. Address:", self.client_address)


    """ sends a message of the form "img_length|img" """
    def send(self, image):
        ret, img_buf = cv2.imencode('.jpg', image)
        img_buf = pickle.dumps(img_buf)
        length = str(len(img_buf)) + '|'
        img_buf = bytes(length, 'utf-8') + img_buf
        self.client.sendall(img_buf)

    def closeClientConnection(self):
        self.client.sendall(b'X')

# Main while loop
def main():
    print("Server opened")

    def display(image, message="Image"):
        if message is not None:
            font = cv2.FONT_HERSHEY_COMPLEX
            color = (255, 0, 255)
            cv2.putText(image, message, (5,15), font, .7, color, 1, cv2.LINE_AA)
            cv2.imshow(message,image)


    WEBCAM = MyCamera(0)

    try:
        connection = TCPServerProtocol()
        connection.listen()
        connection.accept()
        
    except Exception as e:
        print("ERROR: " + str(e))
        return

    while True:
        k = cv2.waitKey(1)
        if k == ord('q'):
            break

        WEBCAM.tick()
        color_frame = WEBCAM.getColorFrame()
        display(color_frame.copy(), 'Press q to take picture to send')
        connection.send(color_frame)
    
    connection.closeClientConnection()



if __name__ == "__main__":
    main()