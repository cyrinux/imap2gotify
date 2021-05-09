# -*- coding: utf8 -*-

import requests
import simplejson as json

from helpers import get_logger


class Gotify:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__, config)
        self.server = config["gotify"]["host"].strip("/")
        self.token = config["gotify"]["token"]

    def send(self, matchResults: list) -> list:
        """Send list of MatchResults to gotify
        returning list of successfully sent EmailStruct"""
        sent_messages = []
        if matchResults and len(matchResults) > 0:
            num_failed = 0
            for match in matchResults:
                if match.matched:
                    response = self._send_to_gotify(match.message, match.rule)
                    if response:
                        sent_messages.append(match.message)
                    else:
                        num_failed += 1
            self.logger.info(
                "Gotify send results: %d sent sucessfully, %d failed to send",
                len(sent_messages),
                num_failed,
            )
        return sent_messages

    @staticmethod
    def _importance_to_priority(importance):
        if importance is None:
            return 1
        elif importance.lower() == "high":
            return 7
        elif importance.lower() == "medium":
            return 4
        elif importance.lower() == "low":
            return 3
        else:
            return 1

    def _send_to_gotify(self, message, rule):
        if rule.priority:
            self.logger.debug("Using rule override priority: %s", rule.priority)
            priority = rule.priority
        else:
            priority = Gotify._importance_to_priority(message.importance)

        if rule.token:
            self.logger.debug("Using rule override token: %s", rule.token)
            token = rule.token
        else:
            token = self.token

        if rule.extras:
            self.logger.debug("Rule extras: %s", rule.extras)
            extras = rule.extras
        else:
            extras = None

        body = {"title": message.subject, "message": message.body, "priority": priority}

        if extras:
            body["extras"] = extras

        self.logger.debug("Gotify post message body: %s", json.dumps(body))
        url = "{0}/message?token={1}".format(self.server, token)
        self.logger.debug("Gotify message url: %s", url)
        response = requests.post(url=url, json=body)

        if response.status_code != 200:
            self.logger.error(
                "Failed to send message UUID: %s to Gotify, status code: %d",
                message.msgid,
                response.status_code,
            )
            return False

        self.logger.debug(
            "Send of email message UUID: %s to gotify with priority: %d was successful",
            message.msgid,
            priority,
        )

        return True
