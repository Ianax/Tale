import random

from tale.base import Living, ParseResult
from tale.util import Context, call_periodically
from tale.lang import capital
from tale.verbdefs import AGGRESSIVE_VERBS


class Cat(Living):
    def init(self) -> None:
        self.aliases = {"cat"}

    @call_periodically(5, 20)
    def do_purr(self, ctx: Context) -> None:
        if random.random() > 0.7:
            self.location.tell("%s purrs happily." % capital(self.title))
        else:
            self.location.tell("%s yawns sleepily." % capital(self.title))
        # it's possible to stop the periodical calling by setting:  call_periodically(0)(Cat.do_purr)

    def notify_action(self, parsed: ParseResult, actor: Living) -> None:
        if actor is self or parsed.verb in self.verbs:
            return  # avoid reacting to ourselves, or reacting to verbs we already have a handler for
        if parsed.verb in ("pet", "stroke", "tickle", "cuddle", "hug", "caress", "rub"):
            self.tell_others("{Actor} curls up in a ball and purrs contently.")
        elif parsed.verb in AGGRESSIVE_VERBS:
            if self in parsed.who_info:   # only give aggressive response when directed at the cat.
                self.tell_others("{Actor} hisses! I wouldn't make %s angry if I were you!" % self.objective)
        elif parsed.verb in ("hello", "hi", "greet", "meow", "purr"):
            self.tell_others("{Actor} stares at {target} incomprehensibly.", target=actor)
        else:
            message = (parsed.message or parsed.unparsed).lower().split()
            if self.name in message or "cat" in message:
                self.tell_others("{Actor} looks up at {target} and wiggles %s tail." % self.possessive, target=actor)


