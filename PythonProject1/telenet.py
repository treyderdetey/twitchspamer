import socket

sock = socket.socket()
sock.connect(("irc.chat.twitch.tv", 6667))

sock.send(b"PASS oauth:TOKEN\r\n")
sock.send(b"NICK urnick\r\n")
sock.send(b"JOIN #chanel\r\n")
sock.send(b"PRIVMSG #chanel :Hello from Python\r\n")

response = sock.recv(2048).decode()
print("Ответ сервера:", response)