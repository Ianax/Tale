import random

from tale.base import Living, ParseResult
from tale.util import Context, call_periodically
from tale.lang import capital
from tale.verbdefs import AGGRESSIVE_VERBS

class Sarah(Living):
    def init(self) -> None:
        super().init()
        self.verbs['ask'] = "Ask Sarah a question"

    def handle_verb(self, parsed, actor):
        if parsed.verb == "ask":
            actor.tell(parsed)
            actor.tell('')

            if 'herself' in parsed.args:
                actor.tell("Ah, how nice. You'd like to know about . . . me.")

        return True

