# -*- coding: utf8 -*-

import os
import requests
import toml


def push(mail, verbose=False):
    config = toml.load([os.path.abspath("config/settings.toml")])

    # Connect to the server
    gotify_server = config["gotify"]["host"]
    if "token" in mail:
        gotify_token = mail["token"]
    else:
        gotify_token = config["gotify"]["token"]

    params = {
        "title": mail["subject"],
        "message": mail["body"],
        "priority": mail["priority"],
        "extras": mail["extras"],
    }

    if verbose:
        import pprint

        pprint.pprint(params)

    r = requests.post(f"{gotify_server}/message?token={gotify_token}", json=params)

    if r.status_code != 200:
        if verbose:
            print("Can't send push notification")
        return False
    print(
        f">>>> Gotify for email: {params['title']} with priority {params['priority']}"
    )
    return True
