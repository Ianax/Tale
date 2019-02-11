#! /usr/bin/env python3
"""
'demo'
by demo - demo@demo.demo
"""

import sys
from tale.story import *


class Story(StoryBase):
    # Create your story configuration and customize it here.
    # Look at the options in StoryConfig to see what you can change.
    config = StoryConfig()
    config.name = "demo"
    config.author = "demo"
    config.author_address = "demo@demo.demo"
    config.version = "1.0"
    config.requires_tale = "4.6.dev0"
    config.supported_modes = {GameMode.IF}
    config.money_type = MoneyType.MODERN
    config.player_money = 100.0
    config.player_name = "jon"
    config.player_gender = "m"
    config.startlocation_player = "house.livingroom"
    config.zones = ["house"]
    # Your story-specific configuration fields should be added below.
    # You can override various methods of the StoryBase class,
    # have a look at the Tale example stories to learn how you can use these.


if __name__ == "__main__":
    # story is invoked as a script, start it.
    from tale.main import run_from_cmdline
    run_from_cmdline(["--game", sys.path[0]])
