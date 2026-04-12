import socket

s = socket.socket()
s.connect(("example.com", 80))
s.sendall(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")

while chunk := s.recv(1024):
    print(chunkimport socket

s = socket.socket()
s.connect(("example.com", 80))
s.sendall(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")

while chunk := s.recv(1024):
    print(chunk))
