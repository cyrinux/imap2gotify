# -*- coding: utf8 -*-

import imaplib
import os
import toml


def open_connection(verbose=False):
    config = toml.load([os.path.abspath("config/settings.toml")])
    imaplib.Debug = config["imap"]["loglevel"] or 1

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


def idle_mail(process_mails):
    config = toml.load([os.path.abspath("config/settings.toml")])
    imaplib.Debug = config["imap"]["loglevel"] or 1
    c = open_connection()
    try:
        c.select("INBOX", readonly=True)
        idle = "{} IDLE\r\n".format(c._new_tag().decode())
        c.send(idle.encode())
        print(">>> waiting for new mail on mailbox...")
        while True:
            line = c.readline().decode().strip()
            if line.startswith("* BYE ") or (len(line) == 0):
                print(">>> leaving...")
                break
            if line.endswith("EXISTS"):
                print(">>> NEW MAIL ARRIVED!")
                process_mails()
    finally:
        try:
            print(">>> closing...")
            c.close()
        except:
            pass
        c.logout()


if __name__ == "__main__":
    c = open_connection(verbose=True)
    try:
        print(c)
    finally:
        c.logout()
        print(">>>> logged out")
