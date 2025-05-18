import socket

def send_data():
    # A C# szerver IP címe és portja
    server_ip = '127.0.0.1'
    server_port = 5000

    # A három paraméter, amit küldeni szeretnénk
    param1 = 10
    param2 = 10
    param3 = -100

    # TCP kapcsolat létrehozása és adatok küldése
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        data = f"{param1};{param2};{param3}"
        s.sendall(data.encode('ascii'))

if __name__ == "__main__":
    send_data()