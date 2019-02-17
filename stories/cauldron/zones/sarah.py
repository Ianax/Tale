import random

from tale.base import Living, ParseResult
from tale.util import Context, call_periodically
from tale.lang import capital
from tale.verbdefs import AGGRESSIVE_VERBS

class Sarah(Living):
    def init(self) -> None:
        super().init()

