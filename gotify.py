# -*- coding: utf8 -*-

import os
import requests
import toml
import simplejson as json


def push(mail, verbose=False):
    config = toml.load([os.path.abspath("config/settings.toml")])
    gotify_server = config["gotify"]["host"]
    gotify_token = config["gotify"]["token"]

    if "token" in mail:
        gotify_token = mail["token"]

    params = {
        "title": mail["subject"],
        "message": mail["body"],
        "priority": mail["priority"],
    }

    if "extras" in mail:
        params["extras"] = mail["extras"]

    if verbose:
        print(json.dumps(params))

    push = requests.post(f"{gotify_server}/message?token={gotify_token}", json=params)

    if push.status_code != 200:
        print(f">>> Error: {push.status_code}")
        return False

    print(
        f">>>> Gotify for email: {params['title']} with priority {params['priority']}"
    )

    return True
