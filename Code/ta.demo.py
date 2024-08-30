from charm.toolbox.pairinggroup import PairingGroup
from charm.core.engine.util import objectToBytes
import socket
import threading
import ssl
import pickle
from c_ta import TA

# Thiết lập thông tin kết nối SSL/TLS
KEYFILE = r"private.key"  # Đường dẫn tới file chứa private key
CERTFILE = r"server.crt"  # Đường dẫn tới file chứa chứng chỉ SSL/TLS

# Cấu hình server
HOST = "127.0.0.1"
PORT = 49999
FORMAT = "utf-8"
BUFFER_SIZE = 1024


def receive_att(conn):
    return pickle.loads(conn.recv(4096))


def handle_client(conn, addr):
    print("client connected:", addr)
    while True:
        msg = conn.recv(1024).decode(FORMAT)
        if msg == "get_pubKey":
            pk = ta.get_pk()
            group = PairingGroup("SS512")
            data = objectToBytes(pk, group)
            conn.sendall(data)
            conn.sendall("__end__".encode(FORMAT))
            print("Sent public key to client", addr)

        elif msg == "gen_secretKey":
            att_list = receive_att(conn)
            print("Received attributes list", att_list, "from", addr)
            sk = ta.keygen(att_list)
            group = PairingGroup("SS512")
            data = objectToBytes(sk, group)
            conn.sendall(data)
            conn.sendall("__end__".encode(FORMAT))
            print("Generate secret key for client", addr)

        else:
            if msg == "x":
                break
            print("client", str(addr) + ":", msg)

    print("client", addr, "disconnected")
    conn.close()


if __name__ == "__main__":
    groupObj = PairingGroup("SS512")
    ta = TA(groupObj)

    ta.setup()
    # print(ta.get_pk(), '\n\n', ta.get_mk())

    # Khởi tạo socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Tạo conntext SSL/TLS
    conntext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    conntext.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    # Cấu hình các tùy chọn bảo mật
    conntext.set_ciphers("ECDHE-RSA-AES128-GCM-SHA256")

    # Gắn conntext vào socket
    ssl_socket = conntext.wrap_socket(s, server_side=True)

    # Bind và lắng nghe kết nối
    ssl_socket.bind((HOST, PORT))
    ssl_socket.listen()

    print("Server", HOST, PORT, "is running...")
    # print('Waiting for clients to connect')

    try:
        while True:
            conn, addr = ssl_socket.accept()
            thr = threading.Thread(target=handle_client, args=(conn, addr))
            thr.daemon = False
            thr.start()

    except Exception as e:
        print("Error:", e)

    finally:
        print("Server terminated.")
        ssl_socket.close()
