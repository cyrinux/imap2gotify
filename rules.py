import logging
from helpers import get_logger
from collections import namedtuple
from collections.abc import MutableMapping
from imap import EmailStruct

Rule = namedtuple('Rule',['name','from_','subject','priority','token','extras'])
MatchResult = namedtuple('MatchResult', ['matched','rule','message'])

class RulesProcessor:
    def __init__(self, config: MutableMapping):
        """ Initializes our RulesProcessor instance from toml config """
        self.config = config
        self.logger = get_logger(__name__,config)
        self.rules = []
        # build list of rules
        for rule_name in self.config["rules"]:
            rule_config = self.config["rules"][rule_name]

            rule = Rule(name=rule_name,
                        from_=rule_config.get('from',None),
                        subject=rule_config.get('subject',None),
                        priority=rule_config.get('priority',None),
                        token=rule_config.get('token',None),
                        extras=rule_config.get('extras',None))
            self.rules.append(rule)


    def check_matches(self,messages: list) -> (list,list):
        """ Runs list of EmailStruct messages through rules
        returning two lists of MatchResults, the first are those that matched a rule,
        the second list of MatchResults are those that did not have a match """
        matches = []
        misses = []
        if (len(messages) > 0):
            for message in messages:
                results = self._is_match(message)
                if results.matched:
                    matches.append(results)
                else:
                    misses.append(results)
                self.logger.debug("Rules match results for message:\n" +
                                "\tuuid: %s\n" +
                                "\tfrom: %s\n" +
                                "\tsubject: %s\n" +
                                "\tmatched: %s\n" +
                                "\tmatched rule: %s\n",
                                message.msgid, message.from_, message.subject,
                                results.matched, results.rule.name if results.rule else None)
            
            self.logger.info('%d of %d messages matched rules',len(matches),len(messages))
        return (matches,misses)


    def _is_match(self, message: EmailStruct) -> MatchResult:
        """ Run given message thru rules returning a
        MatchResult with the results of match processing
        """
        matched = False
        matched_rule = None
        priority = None
        for rule in self.rules:
            # AND matching conditional
            if (rule.from_ is not None and rule.subject is not None and
                rule.from_ in message.from_ and rule.subject in message.subject):
                matched = True
            elif rule.subject is not None and rule.subject in message.subject:
                matched = True
            elif rule.from_ is not None and rule.from_ in message.from_:
                matched = True

            # Set gotify related values for extras and break
            if matched:
                matched_rule = rule
                break

        return MatchResult( matched=matched,
                            rule=matched_rule,
                            message=message)