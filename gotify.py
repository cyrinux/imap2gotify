import configparser
import os
import requests


def push(*params, verbose=False):
    config = configparser.ConfigParser()
    config.read([os.path.abspath("config/settings.ini")])

    # Connect to the server
    gotify_server = config.get("gotify", "host")
    gotify_token = config.get("gotify", "token")

    params = {
        "title": params.title,
        "message": params.message,
        "priority": params.priority,
    }
    r = requests.post(f"{gotify_server}/message?token={gotify_token}", params=params)
    if r.status_code != 200:
        print("Can't send push notification")
        return False
    print(f">>>> Gotify for email: {params.title} with priority {params.priority}")
    return True
