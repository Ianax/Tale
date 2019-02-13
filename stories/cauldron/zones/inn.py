"""
The house, where the player starts the game.
Their pet cat is also here and you can interact with him a little.

The generated demo code below is provided for you to use or modify as you wish.
(it creates a trivial location similar to the built-in demo story of the Tale library itself)
"""

from tale.base import Location, Exit, Door

##### Lobby #####
foyer_descr = """
    The foyer has a warm, dusty feel. Dark wood floors support
    antique furniture. Black laced curtains frame misty windows that prevent
    a clear view outisde.
    """
foyer = Location(name="Foyer",
                 descr=foyer_descr)
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

sitting_room_desc = """This cozy sitting room is warmed by a fire in the
                     fireplace. A long couch and a pair of overstuffed chairs
                     leave a perfect place to sit and get warm. A bookshelf
                     sits in the corner, laden with leather bound books that
                     appear very old."""

sitting_room = Location("Sitting Room", sitting_room_desc)

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

##### Dinning Room #####

dining_room_desc = """This large dining room is set with several tables of various sizes.
                    Fine crystal glasses and silver utensils adorn the tables, and a large
                    fire burns brightly in the fireplace."""

dining_room = Location("Dining Room", dining_room_desc)

dining_sitting = Exit(directions=["west", "sitting"],
                      target_location="inn.sitting_room",
                      short_descr="There is a sitting room to the west.",
                      long_descr="""Through the archway you can see a cozy
                                    room flickering to the light of a fire."""
                      )

dining_room.add_exits([dining_sitting])
