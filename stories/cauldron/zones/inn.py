"""
The house, where the player starts the game.
Their pet cat is also here and you can interact with him a little.

The generated demo code below is provided for you to use or modify as you wish.
(it creates a trivial location similar to the built-in demo story of the Tale library itself)
"""

from tale.base import Location, Exit, Door
from zones.sarah import Sarah
from zones.descriptions import room_descriptions

##### Lobby #####

foyer = Location(name="Foyer",
                 descr=room_descriptions['foyer'])
# Build Exits
foyer_closet = Exit(directions="closet",
                    target_location="inn.foyer_closet",
                    short_descr="There is a small closet in the foyer.",
                    long_descr=None)

foyer_sitting = Exit(directions=["north", "sitting"],
                     target_location="inn.sitting_room",
                     short_descr="There is a sitting room to the north.",
                     long_descr="""Through the archway you can see a cozy
                                   room flickering to the light of a fire."""
                     )

foyer.add_exits([foyer_closet,
                 foyer_sitting])

# Insert items & npcs



##### Foyer Closet #####
foyer_closet = Location("Foyer Closet", "A small closet.")

closet_foyer = Exit(directions=["out", "back", "foyer"],
                    target_location="inn.foyer",
                    short_descr="You can see the foyer you came from.",
                    long_descr=None)

foyer_closet.add_exits([closet_foyer])


##### Sitting Room #####

sitting_room = Location("Sitting Room", room_descriptions['sitting_room'])

sitting_foyer = Exit(directions=["foyer", "south"],
                     target_location="inn.foyer",
                     short_descr="The foyer is to the south.",
                     long_descr=None,
                     )
sitting_dining = Exit(directions=["east", "dining"],
                       target_location="inn.dining_room",
                       short_descr="There appears to be a dinning room to the east.",
                       long_descr="To the east you see a room with tables set to eat.",
                       )

sitting_room.add_exits([sitting_foyer,
                        sitting_dining])

sarah = Sarah(name="Sarah",
              gender="f",
              descr="Sarah sits here casually in a high backed chair."
              )
sitting_room.insert(sarah, None)

##### Dinning Room #####

dining_room = Location("Dining Room", room_descriptions['dining_room'])

dining_sitting = Exit(directions=["west", "sitting"],
                      target_location="inn.sitting_room",
                      short_descr="There is a sitting room to the west.",
                      long_descr="""Through the archway you can see a cozy
                                    room flickering to the light of a fire."""
                      )

dining_room.add_exits([dining_sitting])
