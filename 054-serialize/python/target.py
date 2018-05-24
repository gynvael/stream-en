import pickle
import socket

HOST = '0.0.0.0'
PORT = 1234
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
while 1:
    data = conn.recv(1024)
    if not data: break
    d = pickle.loads(data)
    print d
conn.close()



