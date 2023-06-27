import socket
import json
import os
import threading
import psutil
from datetime import datetime, timedelta
import numpy as np

import random
import string


memory_usage = psutil.virtual_memory()
MEM_SIZE = memory_usage.total / 1024 / 1024 / 1024


# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Variable to store system resource usage
global usage_history

usage_history = dict()
# Variable to store system resource reserved
global reserved_usage
reserved_usage = dict()

lock = threading.Lock()


def get_id():
    # It generate a random string of 16 characters
    letters = (
        string.ascii_letters + string.digits
    )  # include both uppercase and lowercase letters, and digits
    return "".join(random.choice(letters) for _ in range(16))


def update_resource_history(usage_history):
    id_ = int(datetime.now().timestamp() / 60) % 10
    memory_usage = psutil.virtual_memory()
    swap_usage = psutil.swap_memory()
    usage_history[id_] = {
        "cpu": round(psutil.cpu_percent(), 2),
        "mem": round(
            (memory_usage.total - memory_usage.available) / 1024 / 1024 / 1024, 2
        ),
        "swap": round(swap_usage.used / 1024 / 1024 / 1024, 2),
    }


def get_mean_resource_history(usage_history):
    if len(usage_history) == 0:
        0, 0
    # it will keep the last 10 minutes mean (60 -> minutes, 10 -> number of values to keep)
    return (
        round(np.mean([value["cpu"] for value in usage_history.values()]), 2),
        round(np.mean([value["mem"] for value in usage_history.values()]), 2),
        round(np.mean([value["swap"] for value in usage_history.values()]), 2),
    )


def add_resource_reserved(reserved_usage, id_, cpu=0, mem=0, timeout=0):
    date_ = datetime.now() + timedelta(seconds=timeout)
    reserved_usage[id_] = {
        "cpu": round(cpu, 2),
        "mem": round(mem, 2),
        "expiration": date_,
    }


def remove_resource_reserved(reserved_usage, id_):
    if id_ in reserved_usage.keys():
        del reserved_usage[id_]
        return True
    return False


def drop_expired_reserved(reserved_usage):
    date_ = datetime.now()
    reserved_usage = {
        id_: values
        for id_, values in reserved_usage.items()
        if (values["expiration"] > date_) & (id_ != "DIFF")
    }
    return reserved_usage


def get_reserved_resource(reserved_usage):
    if len(reserved_usage) == 0:
        return 0, 0
    mem_ = sum([value["mem"] for value in reserved_usage.values()])
    mem_ = max(min(mem_, MEM_SIZE), 0)
    cpu_ = sum([value["cpu"] for value in reserved_usage.values()])
    cpu_ = max(min(cpu_, 100), 0)
    return cpu_, mem_


def auto_reset(reserved_usage, usage_history):
    now_ = datetime.now()
    id_ = "DIFF"
    cpu_reserved, mem_reserved = get_reserved_resource(reserved_usage)
    cpu_usage, mem_usage, swap_usage = get_mean_resource_history(usage_history)
    date_ = now_ + timedelta(seconds=60)
    cpu_diff = round(cpu_usage - cpu_reserved, 2)
    cpu_diff = max(-100, min(cpu_diff, 100))
    mem_diff = round(mem_usage - mem_reserved, 2)
    mem_diff = max(-MEM_SIZE, min(mem_diff, MEM_SIZE)) + swap_usage
    data_ = {
        "cpu": cpu_diff,
        "mem": mem_diff,
        "expiration": date_,
    }
    if id_ in reserved_usage.keys():
        if reserved_usage[id_]["expiration"] < now_:
            reserved_usage[id_] = data_
    else:
        reserved_usage[id_] = data_
    # print(reserved_usage)


# Function to handle a client connection
def handle_client(client_socket, client_address):
    global reserved_usage
    global usage_history
    while True:
        # Receive data from the client
        data = client_socket.recv(1024).decode("utf-8")
        if not data:
            # No more data from the client, break the loop
            break
        try:
            reserved_usage = drop_expired_reserved(reserved_usage)
            with lock:
                # Parse the received JSON data
                requested = json.loads(data)
                update_resource_history(usage_history)
                auto_reset(reserved_usage, usage_history)
                if requested["method"] == "attach":
                    cpu_free = 100 - psutil.cpu_percent()
                    memory_usage = psutil.virtual_memory()
                    mem_available = memory_usage.available / 1024 / 1024 / 1024
                    reserved_cpu, reserved_mem = get_reserved_resource(reserved_usage)
                    if (
                        ((reserved_cpu + requested["cpu"]) > 100)
                        or ((reserved_mem + requested["mem"]) > MEM_SIZE)
                        or (cpu_free < requested["cpu"])
                        or (requested["mem"] > mem_available)
                    ):
                        response_data = {"status": "rejected"}
                    else:
                        id_ = get_id()
                        add_resource_reserved(
                            reserved_usage,
                            id_,
                            requested["cpu"],
                            requested["mem"],
                            requested["timeout"],
                        )
                        response_data = {"status": "accepted", "id": id_}
                    # Send the response back to the client
                elif requested["method"] == "dettach":
                    id_ = requested["id"]
                    if remove_resource_reserved(reserved_usage, id_):
                        response_data = {"status": "accepted", "id": id_}
                    else:
                        response_data = {"status": "rejected"}
                else:
                    response_data = {"status": "rejected"}
        except Exception as e:
            response_data = {"status": "rejected"}
        response = json.dumps(response_data)
        # print("=====================================")
        # print("reserved:", reserved_usage)
        # print("-------------------------------------")
        # print("usage history:", usage_history)
        # print("=====================================")
        client_socket.send(response.encode("utf-8"))

    # Close the client connection
    client_socket.close()


def run(port):
    host = "127.0.0.1"
    server_socket.bind((host, port))
    # Listen for incoming connections
    server_socket.listen(1)
    print("Server listening on {}:{}".format(host, port))

    while True:
        # Accept a client connection
        # Bind the socket to a specific host and port
        client_socket, client_address = server_socket.accept()

        # Create a new thread to handle the client
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address)
        )
        client_thread.start()
