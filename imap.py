# -*- coding: utf8 -*-

import imaplib
import os
import toml


def open_connection(verbose=False):
    config = toml.load([os.path.abspath("config/settings.toml")])
    imaplib.Debug = config["imap"]["loglevel"] or 0

    # Connect to the server
    hostname = config["imap"]["hostname"]
    if verbose:
        print(f"Connecting to {hostname}")
    connection = imaplib.IMAP4_SSL(hostname)

    # Login to our account
    username = config["imap"]["username"]
    password = config["imap"]["password"]
    if verbose:
        print(f"Logging in as {username}")
    connection.login(username, password)
    return connection


def idle_mail(process):
    config = toml.load([os.path.abspath("config/settings.toml")])
    imaplib.Debug = config["imap"]["loglevel"] or 0
    verbose = config["main"]["verbose"] or False
    folder = config["imap"]["folder"] or "INBOX"

    c = open_connection(verbose=verbose)
    try:
        c.select(folder, readonly=True)
        idle = "{} IDLE\r\n".format(c._new_tag().decode())
        c.send(idle.encode())
        print(f">>> waiting for new mail on mailbox folder {folder}...")
        while True:
            line = c.readline().decode().strip()
            if line.startswith("* BYE ") or (len(line) == 0):
                print(">>> leaving...")
                break
            if line.endswith("EXISTS"):
                if verbose:
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
    config = toml.load([os.path.abspath("config/settings.toml")])
    verbose = config["main"]["verbose"] or False
    c = open_connection(verbose=verbose)
    try:
        print(c)
    finally:
        c.logout()
        print(">>>> logged out")
