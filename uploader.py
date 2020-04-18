import os
import sys
import time

import paramiko
import scp
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

HOST = '127.0.0.1'
USER = 'user'
PASSWORD = 'password'
PORT = 22

WATCH_DIR = '/hoge/fuga/'
REMOTE_DIR = '/hoge/fuga/'

class CreateFileEventHandler(PatternMatchingEventHandler):

    def __init__(self, connection, patterns=['*.ts'], ignore_patterns=None, ignore_directories=True, case_sensitive=False):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.connection = connection

    def on_created(self, event):
        filepath = event.src_path
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        current_time = time.time()
        connection.put(filepath, REMOTE_DIR+"/"+filename)
        elapsed_time = time.time() - current_time

        throughput = filesize/elapsed_time
        
        print(filepath, filesize, elapsed_time, throughput)


if __name__ == "__main__":
    print("Connecting_Remote_Server: ", HOST)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=HOST,username=USER, password=PASSWORD, port=PORT)
    if sys.argv[1] == "-p" and sys.argv[2] == "scp":
        connection = scp.SCPClient(ssh.get_transport())
    elif sys.argv[1] == "-p" and sys.argv[2] == "sftp":
        connection = ssh.open_sftp()
    else:
        print("Usage: python uploader.py -p scp|sftp")
        sys.exit()

    print("Watching_Local_Directory: ", WATCH_DIR)
    handler = CreateFileEventHandler(connection=connection)
    observer = Observer()
    observer.schedule(handler, WATCH_DIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.001)
    except KeyboardInterrupt:
        observer.stop()
        ssh.close()
    observer.join()

