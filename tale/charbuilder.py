"""
Character builder for multi-user mode.

'Tale' mud driver, mudlib and interactive fiction framework
Copyright by Irmen de Jong (irmen@razorvine.net)
"""

from __future__ import absolute_import, print_function, division, unicode_literals
from . import races
from . import lang


class PlayerNaming(object):
    wizard = False
    name = title = gender = race = description =  None
    def apply_to(self, player):
        player.init_race(self.race, self.gender)
        player.init_names(self.name, self.title, self.description, None)
        if self.wizard:
            player.privileges.add("wizard")
        else:
            if "wizard" in player.privileges:
                player.privileges.remove("wizard")


class CharacterBuilder(object):
    def __init__(self, driver):
        self.driver = driver

    def build(self, target_player=None):
        while True:
            choice = self.driver.input("Create default (w)izard, default (p)layer, (c)ustom player? ")
            if choice == "w":
                naming = self.create_default_wizard()
                break
            elif choice == "p":
                naming = self.create_default_player()
                break
            elif choice == "c":
                naming = self.create_player_from_info()
                break
        if target_player:
            naming.apply_to(target_player)
        return naming

    def create_player_from_info(self):
        naming = PlayerNaming()
        while True:
            naming.name = self.driver.input("Name? ")
            if naming.name:
                break
        naming.gender = self.driver.input("Gender m/f/n? ")[0]
        while True:
            self.driver.player.io.output("Player races: " + ", ".join(races.player_races))     # @todo urghhhhh too many indirections
            naming.race = self.driver.input("Race? ")
            if naming.race in races.player_races:
                break
            self.driver.player.io.output("Unknown race, try again.")  # @todo too many interactions
        naming.wizard = self.driver.input("Wizard y/n? ") == "y"
        naming.description = "A regular person."
        if naming.wizard:
            naming.title = "arch wizard " + lang.capital(naming.name)
        return naming

    def create_default_wizard(self):
        #@todo these hardcoded names eventually need to go
        naming = PlayerNaming()
        naming.name = "irmen"
        naming.wizard = True
        naming.description = "This wizard looks very important."
        naming.gender = "m"
        naming.race = "human"
        naming.title = "arch wizard " + lang.capital(naming.name)
        return naming

    def create_default_player(self):
        #@todo these hardcoded names eventually need to go
        naming = PlayerNaming()
        naming.name = "irmen"
        naming.wizard = False
        naming.description = "A regular person."
        naming.gender = "m"
        naming.race = "human"
        return naming
