"""
Single user driver (for interactive fiction).

'Tale' mud driver, mudlib and interactive fiction framework
Copyright by Irmen de Jong (irmen@razorvine.net)
"""

import sys
import time
import threading
from typing import Generator, Optional, Dict, Any, List
from .story import GameMode, TickMethod, StoryConfig
from . import base
from . import charbuilder
from . import driver
from . import errors
from . import lang
from . import pubsub
from . import util
from . import savegames
from .player import PlayerConnection, Player
from .tio import DEFAULT_SCREEN_DELAY
from .tio import iobase


class IFDriver(driver.Driver):
    """
    The Single user 'driver'.
    Used to control interactive fiction where there's only one 'player'.
    """
    def __init__(self, *, screen_delay: int=DEFAULT_SCREEN_DELAY, gui: bool=False, web: bool=False, wizard_override: bool=False) -> None:
        super().__init__()
        self.game_mode = GameMode.IF
        if screen_delay < 0 or screen_delay > 100:
            raise ValueError("invalid delay, valid range is 0-100")
        self.screen_delay = screen_delay
        self.io_type = "console"
        if gui:
            self.io_type = "gui"
        if web:
            self.io_type = "web"
        self.wizard_override = wizard_override

    def start_main_loop(self):
        if self.io_type == "web":
            print("starting '{0}'  v {1}".format(self.story.config.name, self.story.config.version))
            if self.story.config.author_address:
                print("written by {0} - {1}".format(self.story.config.author, self.story.config.author_address))
            else:
                print("written by", self.story.config.author)
        connection = self.connect_player(self.io_type, self.screen_delay)
        if self.wizard_override:
            connection.player.privileges.add("wizard")
        # create the login dialog
        driver.topic_async_dialogs.send((connection, self._login_dialog_if(connection)))
        # the driver mainloop runs in a background thread, the io-loop/gui-event-loop runs in the main thread
        driver_thread = threading.Thread(name="driver", target=self._main_loop_wrapper, args=(connection,))
        driver_thread.daemon = True
        driver_thread.start()
        connection.singleplayer_mainloop()     # this doesn't return!

    def show_motd(self, player: Player, notify_no_motd: bool=False) -> None:
        pass   # no motd in IF mode

    def do_save(self, player: Player) -> None:
        if not self.story.config.savegames_enabled:
            player.tell("It is not possible to save your progress.")
            return
        # XXX bogus data
        locations = frozenset([player.location])
        items = frozenset(player.location.items) | frozenset(player.inventory)
        livings = frozenset(player.location.livings)
        exits = frozenset(player.location.exits.values())
        serializer = savegames.TaleSerializer()
        print("SAVING, PLAYER name={}  title={}".format(player.name, player.title))  # XXX
        savedata = serializer.serialize(self.story.config, player, items, livings, locations, exits, self.deferreds, self.game_clock)
        self.user_resources[util.storyname_to_filename(self.story.config.name) + ".savegame"] = savedata
        player.tell("Game saved.")
        player.tell("<bright><it>NOTE: save games are not yet working reliably!!!</>")   # XXX fix save games.
        if self.story.config.display_gametime:
            player.tell("Game time: %s" % self.game_clock)
        player.tell("\n")

    def connect_player(self, player_io_type: str, line_delay: int) -> PlayerConnection:
        connection = PlayerConnection()
        connect_name = "<connecting_%d>" % id(connection)  # unique temporary name
        new_player = Player(connect_name, "n", race="elemental", descr="This player is still connecting to the game.")
        io = None  # type: iobase.IoAdapterBase
        if player_io_type == "gui":
            from .tio.tkinter_io import TkinterIo
            io = TkinterIo(self.story.config, connection)
        elif player_io_type == "web":
            from .tio.if_browser_io import HttpIo, TaleWsgiApp
            wsgi_server = TaleWsgiApp.create_app_server(self, connection, use_ssl=False, ssl_certs=None)   # you can enable SSL here
            io = HttpIo(connection, wsgi_server)
        elif player_io_type == "console":
            from .tio.console_io import ConsoleIo
            io = ConsoleIo(connection)
            io.install_tab_completion(self)
        else:
            raise ValueError("invalid io type, must be one of: gui web console")
        connection.player = new_player
        connection.io = io
        self.all_players[new_player.name] = connection
        new_player.output_line_delay = line_delay
        connection.clear_screen()
        self.print_game_intro(connection)
        return connection

    def _login_dialog_if(self, conn: PlayerConnection) -> Generator:
        # Interactive fiction (singleplayer): create a player. This is a generator function (async input).
        # Initialize it directly from the story's configuration, load a saved game,
        # or let the user create a new player manually.
        # Be sure to always reference conn.player here (and not get a cached copy),
        # because it will get replaced when loading a saved game!
        if not self.story.config.savegames_enabled:
            load_saved_game = False
        else:
            conn.player.tell("\n")
            load_saved_game = yield "input", ("Do you want to load a saved game ('<bright>n</>' will start a new game)?", lang.yesno)
        conn.player.tell("\n")
        if load_saved_game:
            loaded_player = self._load_saved_game(conn.player)
            if loaded_player:
                # switch active player objects and remove the player placeholder used while connecting
                old_player, conn.player = conn.player, loaded_player
                old_player.destroy(util.Context(self, self.game_clock, self.story.config, conn))
                conn.player.tell("\n")
                prompt = self.story.welcome_savegame(conn.player)
                if prompt:
                    yield "input", "\n" + prompt
                conn.player.tell("\n")
            else:
                load_saved_game = False

        if load_saved_game:
            self.story.init_player(conn.player)
            conn.player.look(short=False)   # force a 'look' command to get our bearings
            return

        if self.story.config.player_name:
            # story config provides a name etc.
            name_info = charbuilder.PlayerNaming()
            name_info.name = self.story.config.player_name
            name_info.stats.race = self.story.config.player_race
            name_info.gender = self.story.config.player_gender
            name_info.money = self.story.config.player_money or 0.0
            name_info.wizard = "wizard" in conn.player.privileges
        else:
            # No story player config: create a character with the builder
            # This is unusual though, normally any 'if' story should provide a player config
            builder = charbuilder.IFCharacterBuilder(conn)
            name_info = yield from builder.build_character()
            if not name_info:
                raise errors.TaleError("should have a name now")

        player = conn.player
        self._rename_player(player, name_info)
        player.tell("\n")
        # move the player to the starting location:
        if "wizard" in player.privileges:
            player.move(self.lookup_location(self.story.config.startlocation_wizard))
        else:
            player.move(self.lookup_location(self.story.config.startlocation_player))
        player.tell("\n")
        prompt = self.story.welcome(player)
        if prompt:
            conn.input_direct("\n" + prompt)   # blocks  (note: cannot use yield here)
        player.tell("\n")
        self.story.init_player(player)
        player.look(short=False)  # force a 'look' command to get our bearings
        conn.write_output()

    def disconnect_idling(self, conn: PlayerConnection):
        pass

    def disconnect_player(self, conn: PlayerConnection):
        raise errors.TaleError("Disconnecting a player should not happen in single player IF mode. Please report this bug.")

    def main_loop(self, conn: PlayerConnection) -> None:
        """
        The game loop, for the single player Interactive Fiction game mode.
        Until the game is exited, it processes player input, and prints the resulting output.
        """
        conn.write_output()
        loop_duration = 0.0
        previous_server_tick = 0.0

        def story_completed():
            self._stop_mainloop = True
            conn.player.tell("\n")
            conn.input_direct("\n\nPress enter to exit. ")  # blocking
            conn.player.tell("\n")
            self._stop_driver()

        while not self._stop_mainloop:
            pubsub.sync("driver-async-dialogs")
            if conn not in self.waiting_for_input:
                conn.write_input_prompt()
            if self.story.config.server_tick_method == TickMethod.COMMAND:
                conn.player.input_is_available.wait()   # blocking wait until playered entered something
                has_input = True
            elif self.story.config.server_tick_method == TickMethod.TIMER:
                # server tick goes on a timer, wait a limited time for player input before going on
                input_wait_time = max(0.01, self.story.config.server_tick_time - loop_duration)
                has_input = conn.player.input_is_available.wait(input_wait_time)
            else:
                raise ValueError("invalid tick method")

            loop_start = time.time()
            if has_input:
                conn.need_new_input_prompt = True
                try:
                    if not conn.player:
                        continue
                    if conn in self.waiting_for_input:
                        # this connection is processing direct input, rather than regular commands
                        dialog, validator, echo_input = self.waiting_for_input.pop(conn)
                        response = conn.player.get_pending_input()[0]
                        if validator:
                            try:
                                response = validator(response)
                            except ValueError as x:
                                prompt = conn.last_output_line
                                conn.io.dont_echo_next_cmd = not echo_input
                                conn.output(str(x) or "That is not a valid answer.")
                                conn.output_no_newline(prompt)   # print the input prompt again
                                self.waiting_for_input[conn] = (dialog, validator, echo_input)   # reschedule
                                continue
                        self._continue_dialog(conn, dialog, response)
                    else:
                        # normal command processing
                        self._server_loop_process_player_input(conn)
                except (KeyboardInterrupt, EOFError):
                    continue
                except errors.SessionExit:
                    self._stop_mainloop = True
                    self.story.goodbye(conn.player)
                    self._stop_driver()
                    break
                except errors.StoryCompleted:
                    story_completed()
                    break
                except Exception:
                    txt = "\n<bright><rev>* internal error (please report this):</>\n" + "".join(util.format_traceback())
                    if conn.player:
                        conn.player.tell(txt, format=False)
                        conn.player.tell("<rev><it>Please report this problem.</>")
                    else:
                        print("ERROR IN SINGLE PLAYER DRIVER LOOP:", file=sys.stderr)
                        print(txt, file=sys.stderr)
                    del txt
            try:
                # sync pubsub pending tells
                pubsub.sync("driver-pending-tells")
                # server TICK
                now = time.time()
                if now - previous_server_tick >= self.story.config.server_tick_time:
                    self._server_tick()
                    previous_server_tick = now
                if self.story.config.server_tick_method == TickMethod.COMMAND:
                    # Even though the server tick may be skipped, the pubsub events
                    # should be processed every player command no matter what.
                    pubsub.sync()
            except errors.StoryCompleted:
                # completing the story can also be done from a deferred action or pubsub event
                story_completed()
                break
            loop_duration = time.time() - loop_start
            self.server_loop_durations.append(loop_duration)
            conn.write_output()

    def _load_saved_game(self, existing_player: Player) -> Optional[Player]:
        # at this time, game loading/saving is only supported in single player IF mode.
        assert len(self.all_players) == 1
        conn = list(self.all_players.values())[0]
        try:
            savegame = self.user_resources[util.storyname_to_filename(self.story.config.name) + ".savegame"].data
            serializer = savegames.TaleSerializer()
            raw_state = serializer.deserialize(savegame)
            del savegame
        except (ValueError, TypeError) as x:
            print("There was a problem loading the saved game data:")
            print(type(x).__name__, x)
            self._stop_driver()
            raise SystemExit(10)
        except FileNotFoundError:
            existing_player.tell("No saved game data found.", end=True)
            return None
        except IOError as x:
            existing_player.tell("Failed to load save game data: "+str(x), end=True)
            return None
        else:
            savegame_version = raw_state["story_config"]["version"]
            if savegame_version != self.story.config.version:
                existing_player.tell("\n")
                existing_player.tell("<it>Note: the saved game data is from a different version of the game and may cause problems.</>")
                existing_player.tell("We'll attempt to load it anyway. (Current game version: %s / Saved game data version: %s). "
                                     % (self.story.config.version, savegame_version), end=True)
            objects_finder = SavegameExistingObjectsFinder()
            state = serializer.recreate_classes(raw_state, objects_finder)
            # Because loading a complete saved game is strictly for single player 'if' mode,
            # we load a new player and simply replace all players with this one.
            import pprint; pprint.pprint(state)  # XXX
            player_info = state["player"]
            deferreds = state["deferreds"]    # XXX convert
            clock = state["clock"]    # XXX convert
            storyconfig = state["story_config"]    # XXX convert

            # sanity checks before we go on
            # XXX assert isinstance(deferreds, list)
            # XXX assert isinstance(clock, util.GameDateTime)
            # XXX assert isinstance(storyconfig, StoryConfig)

            new_player = objects_finder.hookup_player(player_info, state["items"])

            self.all_players = {new_player.name: conn}
            # XXX self.deferreds = deferreds
            # XXX self.game_clock = clock
            # XXX self.story.config = storyconfig
            self.waiting_for_input = {}   # can't keep the old waiters around
            new_player.tell("\n")
            new_player.tell("Game loaded.")
            new_player.tell("<bright><it>NOTE: save games are not yet working reliably!!!</>")  # XXX fix save games.
            if self.story.config.display_gametime:
                new_player.tell("Game time: %s" % self.game_clock)
                new_player.tell("\n")
            if self.wizard_override:
                new_player.privileges.add("wizard")
            return new_player


class SavegameExistingObjectsFinder:
    def item(self, vnum: int, name: str, classname: str) -> base.Item:
        pass  # XXX

    def living(self, vnum: int, name: str, classname: str) -> base.Living:
        pass  # XXX

    def resolve_location_ref(self, vnum: int, name: str, classname: str) -> base.Location:
        loc = base.MudObject.all_locations.get(vnum, None)
        if not loc:
            raise errors.TaleError("location vnum not found: "+str(vnum))
        if loc.name != name or savegames.qual_classname(loc) != classname:
            raise errors.TaleError("location inconsistency for vnum "+str(vnum))
        return loc

    def resolve_item_ref(self, vnum: int, name: str, classname: str, new_items: List[Dict[str, Any]]) -> base.Item:
        item = base.MudObject.all_items.get(vnum, None)
        if not item:
            for ni in new_items:
                if ni["old_vnum"] == vnum:
                    item = ni["item"]
                    if item.name == name and savegames.qual_classname(item) == classname:
                        return item
                    else:
                        raise errors.TaleError("item name/class inconsistency for old_vnum "+str(vnum))
            raise LookupError("item vnum not found: "+str(vnum))
        if item.name != name or savegames.qual_classname(item) != classname:
            raise errors.TaleError("item inconsistency for vnum "+str(vnum))
        return item

    def hookup_player(self, player_info: Dict[str, Any], new_items: Dict[str, Any]) -> Player:
        new_player = player_info["player"]
        assert isinstance(new_player, Player)
        new_player.known_locations = {self.resolve_location_ref(*ref) for ref in player_info["known_locs"]}
        inv = [self.resolve_item_ref(*ref, new_items) for ref in player_info["inventory"]]
        for thing in inv:
            if thing.contained_in and thing.contained_in is not new_player:
                # remove the item from its original location, the player now has it in its pocketses
                thing.contained_in.remove(thing, None)
        new_player.init_inventory(inv)
        loc = self.resolve_location_ref(*player_info["location"])
        loc.insert(new_player, None)
        return new_player
