#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import os
import sys
from collections.abc import MutableMapping

import toml

from gotify import Gotify
from imap import Imap
from rules import RulesProcessor


class Imap2Gotify:
    def __init__(self, config: MutableMapping):
        """Initialize our Imap2Gotify instance using toml config"""
        self.config = config

    def run(self):
        """Process unread emails and then go into IDLE loop waiting for
        notification of new messages arriving, never to return except
        upon KeyboardInterrupt"""
        while True:
            try:
                client = Imap(self.config)
                rules = RulesProcessor(self.config)
                gotify = Gotify(self.config)

                # gets new messages, runs against the rules, marks new that dont
                # match a rule as read, sents matched messages to gotify,
                # those messages that were succefully sent via gotify are
                # then marked as read
                new_messages = client.get_unread()
                (matched_messages, not_matched_messages) = rules.check_matches(
                    new_messages
                )
                client.mark_as_read(not_matched_messages)
                if matched_messages:
                    gotify_sent_messages = gotify.send(matched_messages)
                    client.mark_as_read(gotify_sent_messages)

                # Go into idle waiting for new emails
                client.wait_for_new()

            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    try:
        config = toml.load([os.path.abspath("config/settings.toml")])
    except FileNotFoundError:
        logging.error("No config/settings.toml file was found, terminating")
        sys.exit(1)

    processor = Imap2Gotify(config)
    processor.run()
