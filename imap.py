# -*- coding: utf8 -*-

from imapclient import IMAPClient
from imapclient.exceptions import LoginError
from email.header import decode_header, make_header
from email import message_from_bytes, policy
from email.parser import Parser


import os

import toml
from helpers import get_logger

from collections import namedtuple
from collections.abc import MutableMapping

EmailStruct = namedtuple('EmailStruct', ['msgid','from_','subject','body','importance'])

class Imap:
    def __init__(self,config: MutableMapping):
        """ Initialize our Imap instance with our toml config """
        self.config = config
        self.logger = get_logger(__name__,config)
        self.hostname = self.config["imap"]["hostname"]
        self.username = self.config["imap"]["username"]
        self.password = self.config["imap"]["password"]
        self.folder = self.config["imap"].get("folder","INBOX")
        self.timeout = int(self.config["imap"].get("timeout","300"))
        self._client = None


    def _connect(self,readonly: bool=False):
        """ Opens our imap client connection if it doesnt 
        exist already """
        if self._client is None:
            # Connect to the server
            self.logger.debug("Connecting to %s", self.hostname)
            self._client = IMAPClient(self.hostname)

            # Login to our account
            self.logger.debug("Logging in as %s", self.username)
            try:
                self._client.login(self.username, self.password)
            except LoginError:
                self._client.exception("message")
                return None

            # Select our folder
            self._client.select_folder(self.folder,readonly)

    def close(self):
        """ Close our imap client connection via logout if
        it exists """
        if self._client is not None:
            self.logger.debug("Sending logout")
            try:
                self._client.logout()
            except:
                self.logger.exception("message")
            
            self._client = None


    def _get_messages(self,msg_ids: list) -> list:
        """ Returns EmailStruct named tuples from given list message id list """
        emails = []
        if (len(msg_ids) > 0):
            self.logger.debug("Fetching %s messages", len(msg_ids))
            results = self._client.fetch(msg_ids, "RFC822")
            for msgid, raw_msg in results.items():
                self.logger.debug("Decoding message headers and body")
                msg = message_from_bytes(raw_msg[b'RFC822'],policy=policy.default)
                emails.append(EmailStruct(  msgid=msgid,
                                            from_=msg.get("from"),
                                            subject=str(make_header(decode_header(msg.get("subject")))),
                                            body=msg.get_body(preferencelist=('plain')).get_content(),
                                            importance=msg.get("importance")
                                            )
                            )
        return emails

    def get_unread(self) -> list:
        """ Returns list of EmailStruct messages that are marked 
           unseen (unread) message in the selected folder
           Returns None on error"""
        self._connect()
        # Can't connect, return None
        if self._client is None:
            self.logger.warning("Client not connected")
            return None
        msg_ids = self._client.search(["UNSEEN"])
        num_unread = len(msg_ids)
        if num_unread == 0:
            self.logger.info("No unread flagged messages found")
        else:
            self.logger.info("%d unread flagged message(s) found, getting headers", len(msg_ids))

        return self._get_messages(msg_ids)


    def mark_as_read(self,emails: list):
        """ Marks given list of EmailStruct messages as seen """
        if (emails and len(emails) > 0):
            self._connect()
            msg_ids = [e.msgid for e in emails]
            num_msgs = len(msg_ids)
            if num_msgs > 0:
                self.logger.info("Marking %d message(s) as read", num_msgs)
                self._client.set_flags(msg_ids,"\\SEEN",silent=True)


    def wait_for_new(self) -> bool:
        """ IDLE waits for new messages to arrive for the
        specified timeout (in seconds), then returns 
        True if new messages exist, otherwise False """
        self._connect()
        self._client.idle()
        new_exist = False
        self.logger.info("Waiting idle for new messages to arrive, %d second timeout", self.timeout)
        while True:
            # todo add an overall breakout time check
            responses = self._client.idle_check(timeout=self.timeout)

            if self._search_responses(b'EXISTS',responses):
                self.logger.info("New messages have arrived")
                new_exist = True
                break
            if self._search_responses(b'BYE',responses):
                self.logger.info("Server issued logout, closing connection")
                break
            if len(responses) == 0:
                # Idle check timed out
                self.logger.info("Timeout occured, closing connection")
                break
            else:
                self.logger.debug("Ignoring responses:")
                self.logger.debug(responses)

        # cleanup/close our session
        if self._client:
            self._client.idle_done()
        self.close()

        return new_exist

    def _search_responses(self,lookfor: str,responses: list) -> bool:
        """ Search varied length tuples in a list, seaching for lookfor
        string, returning True if exists somewhere in the list of tuples,
        otherwise, returns False """
        return len([resp for resp in responses if lookfor in resp]) > 0