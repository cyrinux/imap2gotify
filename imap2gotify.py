#!/usr/bin/env python3
# -*- coding: utf8 -*-

import email
import email.message
import email.parser
import gotify
import imap
import os
import toml
from email.header import decode_header


def get_body(msg):
    if msg.is_multipart():
        body = get_body(msg.get_payload(0))
        try:
            body = body.decode("latin-1").encode("utf8")
        except:
            pass
        return body
    else:
        return msg.get_payload(None, True)


def get_subject(msg):
    try:
        h = decode_header(msg.get("subject"))
        return h[0][0].decode("latin-1").encode("utf8")
    except:
        return msg.get("subject")


def process_rules(mail, verbose=False):
    config = toml.load([os.path.abspath("config/settings.toml")])
    for r in config["rules"]:
        rule = config["rules"][r]
        match = False

        if all(k in rule for k in ("from", "subject")):
            if rule["from"] in mail["from"]:
                if rule["subject"] in mail["subject"]:
                    match = True

        elif any(k in rule for k in ("from", "subject")):
            if "subject" in rule and rule["subject"] in mail["subject"]:
                match = True

            elif "from" in rule and rule["from"] in mail["from"]:
                match = True

        if match:
            mail["priority"] = rule["priority"]

            if "token" in rule:
                if verbose:
                    print(rule["token"])
                mail["token"] = rule["token"]

            if "extras" in rule:
                if verbose:
                    print(rule["extras"])
                mail["extras"] = rule["extras"]

            print(
                f">>> Mail processed, from: {mail['from']}, subject: {mail['subject']}, priority: {mail['priority']}"
            )

            return mail


def main_loop(verbose=False):
    c = imap.open_connection()
    c.select("INBOX")

    # fetch unseen
    _, data = c.search(None, "UnSeen")
    print(">>> MAIN LOOP")

    # read each new mail and send alert
    for num in data[0].split():
        _, data = c.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        mail = {
            "body": get_body(msg),
            "from": msg.get("from"),
            "priority": 1,
            "subject": get_subject(msg),
        }

        mail_keep = process_rules(mail, verbose)

        # send notication
        if mail_keep:
            r = gotify.push(mail_keep)
            if r:
                # mark as read
                c.store(num, "+FLAGS", "(\\Seen)")
        else:
            c.store(num, "+FLAGS", "(\\Seen)")
            print(f"ignoring {mail}")


if __name__ == "__main__":
    imap.idle_mail(main_loop)
