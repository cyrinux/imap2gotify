# -*- coding: utf8 -*-

import imaplib
import os
import toml


class Imap:
    def __init__(self):
        self.config = toml.load([os.path.abspath("config/settings.toml")])
        self.hostname = self.config["imap"]["hostname"]
        self.username = self.config["imap"]["username"]
        self.password = self.config["imap"]["password"]

        self.verbose = False
        if "verbose" in self.config["main"]:
            self.verbose = self.config["main"]["verbose"]

        self.folder = "INBOX"
        if "folder" in self.config["imap"]:
            self.folder = self.config["imap"]["folder"]

        self.loglevel = 0
        if "loglevel" in self.config["imap"]:
            self.loglevel = self.config["imap"]["loglevel"] or 0

    def open_connection(self):
        imaplib.Debug = self.loglevel

        # Connect to the server
        if self.verbose:
            print(f"Connecting to {self.hostname}")
        connection = imaplib.IMAP4_SSL(self.hostname)

        # Login to our account
        if self.verbose:
            print(f"Logging in as {self.username}")
        connection.login(self.username, self.password)
        return connection

    def idle_mail(self, process):
        imaplib.Debug = self.loglevel
        c = self.open_connection()

        try:
            c.select(self.folder, readonly=True)
            idle = "{} IDLE\r\n".format(c._new_tag().decode())
            c.send(idle.encode())
            print(f">>> waiting for new mail on mailbox folder {self.folder}...")
            while True:
                line = c.readline().decode().strip()
                if line.startswith("* BYE ") or (len(line) == 0):
                    print(">>> leaving...")
                    break
                if line.endswith("EXISTS"):
                    if self.verbose:
                        print(">>> NEW MAIL ARRIVED!")
                    try:
                        process()
                    except Exception as e:
                        print(e)

        finally:
            try:
                print(">>> closing...")
                c.close()
            except:
                pass
            c.logout()


if __name__ == "__main__":
    imap = Imap()
    c = imap.open_connection()
    try:
        print(c)
    finally:
        c.logout()
        print(">>>> logged out")
