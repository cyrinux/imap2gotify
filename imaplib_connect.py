# -*- coding: utf8 -*-

import imaplib
import configparser
import os


def open_connection(verbose=False):
    # Read the config file
    config = configparser.ConfigParser()
    config.read([os.path.abspath("config/settings.ini")])

    # Connect to the server
    hostname = config.get("imap", "hostname")
    if verbose:
        print(f"Connecting to {hostname}")
    connection = imaplib.IMAP4_SSL(hostname)

    # Login to our account
    username = config.get("imap", "username")
    password = config.get("imap", "password")
    if verbose:
        print(f"Logging in as {username}")
    connection.login(username, password)
    return connection


if __name__ == "__main__":
    c = open_connection(verbose=True)
    try:
        print(c)
    finally:
        c.logout()
        print("logged out")
