"""
The house, where the player starts the game.
Their pet cat is also here and you can interact with him a little.

The generated demo code below is provided for you to use or modify as you wish.
(it creates a trivial location similar to the built-in demo story of the Tale library itself)
"""

import random

from tale.base import Location, Exit, Door, Key, Living, ParseResult
from tale.errors import StoryCompleted
from tale.lang import capital
from tale.player import Player
from tale.util import Context, call_periodically
from tale.items.basic import elastic_band, woodenYstick
from tale.verbdefs import AGGRESSIVE_VERBS

# define items and NPCs

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


cat = Cat("garfield", "m", race="cat", descr="A very obese cat, orange and black. It looks tired, but glances at you happily.")
key = Key("key", "small rusty key", descr="This key is small and rusty. It has a label attached, reading \"garden door\".")

# define the various locations

class GameEnd(Location):
    def notify_player_arrived(self, player: Player, previous_location: Location) -> None:
        # player has entered, and thus the story ends
        player.tell("\n")
        player.tell("\n")
        player.tell("<bright>Congratulations on escaping the house!</> Someone else has to look after Garfield now though...")
        raise StoryCompleted


# Create location

##### Living Room #####
livingroom_descr = """
    The living room in your home in the outskirts of the city."""
livingroom = Location(name="Living room",
                      descr=livingroom_descr)
# Build Exits
garden_door = Door(
    directions=["garden", "door"],
    target_location="house.outside",
    short_descr="A door leads to the garden.",
    long_descr="There's a heavy door here that leads to the garden outside the house.",
    locked=True, opened=False, key_code="1")

lr_closet = Exit(directions="closet",
                 target_location="house.closet",
                 short_descr="There is a small closet in your house.",
                 long_descr=None)

livingroom.add_exits([garden_door,
                      lr_closet])

# Insert items & npcs
livingroom.insert(cat, None)
livingroom.insert(elastic_band.clone(), None)

##### Closet #####
closet = Location("Closet", "A small room.")

closet_lr = Exit(directions=["living room", "back", "livingroom"],
                 target_location="house.livingroom",
                 short_descr="You can see the living room where you came from.",
                 long_descr=None)

closet.add_exits([closet_lr])

closet.insert(key, None)
key.key_for(garden_door)

closet.insert(woodenYstick.clone(), None)

##### Outside #####

outside = GameEnd("Outside", "It is beautiful weather outside.")
