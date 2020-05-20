#!/usr/bin/env python3
# -*- coding: utf8 -*-

import imap
import gotify
import email
import email.parser
import email.message


def get_text(msg):
    if msg.is_multipart():
        return get_text(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


def main_loop():
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
            "subject": msg.get("subject"),
            "from": msg.get("from"),
            "body": get_text(msg),
        }
        # TODO: better priority management
        mail["priority"] = 1
        if "dailymotion.com" in mail["from"]:
            if "CRITICAL" in mail["subject"]:
                mail["priority"] = 10

        print(
            f"from: {mail['from']}, subject: {mail['subject']}, priority: {mail['priority']}"
        )

        # send notication
        r = gotify.push(mail)
        if r:
            # mark as read
            c.store(num, "+FLAGS", "(\\Seen)")


if __name__ == "__main__":
    imap.idle_mail(main_loop)
