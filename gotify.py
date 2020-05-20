# -*- coding: utf8 -*-

import os
import requests
import toml


def push(mail, verbose=False):
    config = toml.load([os.path.abspath("config/settings.toml")])

    gotify_server = config["gotify"]["host"]
    if "token" in mail:
        gotify_token = mail["token"]
    else:
        gotify_token = config["gotify"]["token"]

    params = {
        "title": mail["subject"],
        "message": mail["body"],
        "priority": mail["priority"],
    }

    if "extras" in mail:
        params["extras"] = mail["extras"]

    if verbose:
        print(params)

    push = requests.post(f"{gotify_server}/message?token={gotify_token}", json=params)

    if push.status_code != 200:
        return False

    print(
        f">>>> Gotify for email: {params['title']} with priority {params['priority']}"
    )
