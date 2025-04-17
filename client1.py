import socket
import threading
import sys
from util import make_message, make_packet

def listen_for_messages(sock):
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            tokens = data.decode().split()
            if tokens[0] == '3':  # response_users_list
                print("list:", ' '.join(tokens[3:]))
            elif tokens[0] == '4':  # forward message
                print(f"msg: {tokens[3]}: {' '.join(tokens[4:])}")
            elif tokens[0] == '2':
                reason = tokens[2]
                if reason == 'err_username_unavailable':
                    print("disconnected: username not available")
                elif reason == 'err_server_full':
                    print("disconnected: server full")
                elif reason == 'err_unknown_message':
                    print("disconnected: server received an unknown command")
                break
        except OSError:
            # This happens when socket is already closed
            break
        except:
            break


def send_loop(sock, server_address, username):
    while True:
        try:
            cmd = input().strip()
            if cmd.startswith("msg "):
                tokens = cmd.split()
                if len(tokens) < 4:
                    print("incorrect userinput format")
                    continue
                try:
                    num = int(tokens[1])
                except:
                    print("incorrect userinput format")
                    continue

                if len(tokens) < 2 + num + 1:
                    print("incorrect userinput format")
                    continue

                recipients = tokens[2:2 + num]
                message = ' '.join(tokens[2 + num:])
                if not message:
                    print("incorrect userinput format")
                    continue

                content = f"{username} {num} {' '.join(recipients)} {message}"
                msg = make_message(4, content)
                sock.sendto(msg.encode(), server_address)

            elif cmd == "list":
                content = f"{username} request_users_list"
                msg = make_message(2, content)
                sock.sendto(msg.encode(), server_address)

            elif cmd == "help":
                print("msg <number_of_users> <username1> ... <message>")
                print("list")
                print("help")
                print("quit")

            elif cmd == "quit":
                print("quitting")
                msg = make_message(1, f"{username} disconnect")
                sock.sendto(msg.encode(), server_address)
                sock.close()
                exit(0)

            else:
                print("incorrect userinput format")
        except Exception as e:
            print("Error:", e)
            break



def main():
    if len(sys.argv) != 5 or sys.argv[1] != "-p" or sys.argv[3] != "-u":
        print("Usage: python3 client_1.py -p <server_port> -u <username>")
        sys.exit(1)

    server_port = int(sys.argv[2])
    username = sys.argv[4]
    server_address = ('localhost', server_port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 0))  # Bind to any available port

    # Send join
    join_msg = make_message(1, f"{username} join")
    sock.sendto(join_msg.encode(), server_address)

    threading.Thread(target=listen_for_messages, args=(sock,), daemon=True).start()
    send_loop(sock, server_address, username)

if __name__ == "__main__":
    main()
