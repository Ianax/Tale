#! /usr/bin/env python3
"""
'onyx_keep'
by Kyle - kyle@kyle.kyle
"""

import sys
from tale.story import *


class Story(StoryBase):
    # Create your story configuration and customize it here.
    # Look at the options in StoryConfig to see what you can change.
    config = StoryConfig()
    config.name = "onyx_keep"
    config.author = "Kyle"
    config.author_address = "kyle@kyle.kyle"
    config.version = "1.0"
    config.requires_tale = "4.6.dev0"
    config.supported_modes = {GameMode.IF}
    config.money_type = MoneyType.FANTASY
    config.player_money = 100.0
    config.player_name = "Edward"
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
