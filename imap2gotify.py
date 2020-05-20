#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import imaplib
import imaplib_connect
import email
import email.parser
import email.message
import pprint
import requests
import configparser


def idle_mail():
    config = configparser.ConfigParser()
    config.read([os.path.abspath("config/settings.ini")])
    email_to = config.get("imap", "username")

    # imaplib.Debug = 4
    c = imaplib_connect.open_connection()
    try:
        c.select("INBOX", readonly=True)
        idle = "{} IDLE\r\n".format(c._new_tag().decode())
        c.send(idle.encode())
        print(f">>> waiting for new mail on mailbox {email_to}...")
        while True:
            line = c.readline().decode().strip()
            if line.startswith("* BYE ") or (len(line) == 0):
                print(">>> leaving...")
                break
            if line.endswith("EXISTS"):
                print(">>> NEW MAIL ARRIVED!")
                main_loop()
    finally:
        try:
            print(">>> closing...")
            c.close()
        except:
            pass
        c.logout()


def get_text(msg):
    if msg.is_multipart():
        return get_text(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


def gotify_push(title, message, priority):
    config = configparser.ConfigParser()
    config.read([os.path.abspath("config/settings.ini")])

    # Connect to the server
    gotify_server = config.get("gotify", "host")
    gotify_token = config.get("gotify", "token")

    params = {"title": title, "message": message, "priority": priority}
    r = requests.post(f"{gotify_server}/message?token={gotify_token}", params=params)
    if r.status_code != 200:
        print("Can't send push notification")
        return False
    print(f">>>> Gotify for email: {title} with priority {priority}")
    return True


def main_loop():
    imaplib.Debug = 4
    c = imaplib_connect.open_connection()
    c.select("INBOX")

    # fetch unseen
    _, data = c.search(None, "UnSeen")

    print(">>> MAIN LOOP")

    # read each new mail and send alert
    for num in data[0].split():
        _, data = c.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        email_subject = msg.get("subject")
        email_from = msg.get("from")
        email_body = get_text(msg)
        print(f"from: {email_from}, subject: {email_subject}")
        # if main come from dailymotion
        priority = 1
        if "dailymotion.com" in email_from:
            if 'CRITICAL' in email_subject:
                priority = 10

        # send notication
        r = gotify_push(
            title=email_subject, message=email_body, priority=priority
        )  # TODO: priority
        if r:
            # mark as read
            c.store(num, "+FLAGS", "(\\Seen)")


idle_mail()
