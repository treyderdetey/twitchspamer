import socket
import time

def send_test_message():
    oauth = "oauth:token"
    username = "chanel"
    channel = "chanel"
    message = "Test message from script"

    sock = socket.socket()
    sock.connect(("irc.chat.twitch.tv", 6667))
    sock.send(f"PASS {oauth}\r\n".encode())
    sock.send(f"NICK {username}\r\n".encode())
    sock.send(f"JOIN #{channel}\r\n".encode())
    time.sleep(2)
    sock.send(f"PRIVMSG #{channel} :{message}\r\n".encode())
    print("Message sent. Check the chat.")

send_test_message()