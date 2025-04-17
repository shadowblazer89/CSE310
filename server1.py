import socket
import sys
from util import make_message, MAX_NUM_CLIENTS

clients = {}  # username -> (ip, port)

def handle_join(tokens, addr, sock):
    username = tokens[2]  # Correct now
    if username in clients:
        msg = make_message(2, 'err_username_unavailable')
        sock.sendto(msg.encode(), addr)
        print("disconnected: username not available")
    elif len(clients) >= MAX_NUM_CLIENTS:
        msg = make_message(2, 'err_server_full')
        sock.sendto(msg.encode(), addr)
        print("disconnected: server full")
    else:
        clients[username] = addr
        print(f"join: {username}")



def handle_list(username, addr, sock):
    print(f"request_users_list: {username}")
    users = sorted(clients.keys())
    list_data = f"{len(users)} {' '.join(users)}"
    msg = make_message(3, list_data)
    sock.sendto(msg.encode(), addr)

def handle_msg(tokens, addr, sock):
    try:
        sender = tokens[2]
        num_users = int(tokens[3])
        recipients = tokens[4:4 + num_users]
        message = ' '.join(tokens[4 + num_users:])

        for r in set(recipients):
            if r in clients:
                # Forward to that user
                forward = f"4 {len(sender + ' ' + message)} 1 {sender} {message}"
                sock.sendto(forward.encode(), clients[r])
            else:
                print(f"msg: {sender} to non-existent user {r}")

        print(f"msg: {sender}")

    except Exception as e:
        print(f"disconnected: {tokens[2]} sent unknown command")
        error_msg = make_message(2, 'err_unknown_message')
        sock.sendto(error_msg.encode(), addr)


def handle_disconnect(username):
    if username in clients:
        del clients[username]
        print(f"disconnected: {username}")

def main():
    port = int(sys.argv[2])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', port))

    while True:
        data, addr = sock.recvfrom(1024)
        print("[SERVER RECEIVED]:", data.decode())
        tokens = data.decode().split()

        if not tokens:
            continue

        msg_type = tokens[0]
        for i in range(len(tokens)):
            print(i," ", tokens[i])

        if msg_type == '1':
            if tokens[3] == 'join':
                handle_join(tokens, addr, sock)
            elif tokens[3] == 'disconnect':
                handle_disconnect(tokens[2])

        elif msg_type == '2':  # list or help or unknown
            if tokens[3] == 'request_users_list':
                handle_list(tokens[2], addr, sock)
            else:
                print(f"disconnected: {tokens[2]} sent unknown command")
        elif msg_type == '4':  # message
            handle_msg(tokens, addr, sock)

if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != "-p":
        print("Usage: python3 server_1.py -p <port>")
        sys.exit(1)
    main()
