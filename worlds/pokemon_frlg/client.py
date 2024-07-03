from typing import TYPE_CHECKING, Dict, List, Set, Tuple
from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from .data import data
from .items import reverse_offset_item_value
from .locations import offset_flag

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext


BASE_ROM_NAME: Dict[str, str] = {
    "firered": "pokemon red version",
    "leafgreen": "pokemon green version"
}


EXPECTED_ROM_NAME: Dict[str, str] = {
    "firered": "pokemon red version / AP",
    "leafgreen": "pokemon green version / AP",
    "firered_rev1": "pokemon red version / AP Rev 1",
    "leafgreen_rev1": "pokemon green version / AP Rev 1",
}


DEFEATED_CHAMPION_FLAGS: List[int] = {
    data.constants["TRAINER_FLAGS_START"] + data.constants["TRAINER_CHAMPION_FIRST_BULBASAUR"],
    data.constants["TRAINER_FLAGS_START"] + data.constants["TRAINER_CHAMPION_FIRST_CHARMANDER"],
    data.constants["TRAINER_FLAGS_START"] + data.constants["TRAINER_CHAMPION_FIRST_SQUIRTLE"]
}


TRACKER_EVENT_FLAGS = [
    "FLAG_DEFEATED_BROCK",
    "FLAG_DEFEATED_MISTY",
    "FLAG_DEFEATED_LT_SURGE",
    "FLAG_DEFEATED_ERIKA",
    "FLAG_DEFEATED_KOGA",
    "FLAG_DEFEATED_SABRINA",
    "FLAG_DEFEATED_BLAINE",
    "FLAG_DEFEATED_LEADER_GIOVANNI",
    "FLAG_DELIVERED_OAKS_PARCEL",
    "FLAG_DEFEATED_ROUTE22_RIVAL",
    "FLAG_GOT_SS_TICKET",  # Saved Bill in the Route 25 Sea Cottage
    "FLAG_RESCUED_MR_FUJI",
    "FLAG_HIDE_SAFFRON_ROCKETS",  # Liberated Silph Co.
    "FLAG_SYS_CAN_LINK_WITH_RS",  # Restored Pokemon Network Machine
    "FLAG_RESCUED_LOSTELLE",
    "FLAG_SEVII_DETOUR_FINISHED",  # Gave Meteorite to Lostelle's Dad
    "FLAG_HIDE_RUIN_VALLEY_SCIENTIST",  # Helped Lorelei in Icefall Cave
    "FLAG_LEARNED_YES_NAH_CHANSEY",
    "FLAG_DEFEATED_CHAMP",
    "FLAG_PURCHASED_LEMONADE"
]
EVENT_FLAG_MAP = {data.constants[flag_name]: flag_name for flag_name in TRACKER_EVENT_FLAGS}


class PokemonFRLGClient(BizHawkClient):
    game = "Pokemon FireRed and LeafGreen"
    system = "GBA"
    patch_suffix = (".apfirered", ".apleafgreen", ".apfireredrev1", ".apleafgreenrev1")
    game_version: str
    local_checked_locations: Set[int]
    local_set_events: Dict[str, bool]
    caught_pokemon: int

    def __init__(self) -> None:
        super().__init__()
        self.game_version = None
        self.local_checked_locations = set()
        self.local_set_events = {}
        self.caught_pokemon = 0

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        from CommonClient import logger

        try:
            # Check rom name and patch version
            rom_name_bytes = (await bizhawk.read(ctx.bizhawk_ctx, [(0x108, 32, "ROM")]))[0]
            rom_name = bytes([byte for byte in rom_name_bytes if byte != 0]).decode("ascii")
            if not (rom_name.startswith(BASE_ROM_NAME["firered"]) or rom_name.startswith(BASE_ROM_NAME["leafgreen"])):
                return False
            if rom_name == BASE_ROM_NAME["firered"] or rom_name == BASE_ROM_NAME["leafgreen"]:
                logger.info("ERROR: You appear to be running an unpatched version of Pokemon FireRed or LeafGreen."
                            "You need to generate a patch file and use it to create a patched ROM.")
                return False
            if not (rom_name.startswith(EXPECTED_ROM_NAME["firered"]) or
                    rom_name.startswith(EXPECTED_ROM_NAME["leafgreen"])):
                logger.info("ERROR: The patch file used to create this ROM is not compatible with "
                            "this client. Double check your client version against the version being "
                            "used by the generator.")
                return False
        except UnicodeDecodeError:
            return False
        except bizhawk.RequestFailedError:
            return False  # Should verify on the next pass

        ctx.game = self.game
        ctx.items_handling = 0b001
        ctx.want_slot_data = True
        ctx.watcher_timeout = 0.

        if rom_name == EXPECTED_ROM_NAME["firered"]:
            self.game_version = "firered"
        elif rom_name == EXPECTED_ROM_NAME["leafgreen"]:
            self.game_version = "leafgreen"
        elif rom_name == EXPECTED_ROM_NAME["firered_rev1"]:
            self.game_version = "firered_rev1"
        elif rom_name == EXPECTED_ROM_NAME["leafgreen_rev1"]:
            self.game_version = "leafgreen_rev1"

        return True

    async def set_auth(self, ctx: "BizHawkClientContext") -> None:
        import base64
        auth_raw = (await bizhawk.read(ctx.bizhawk_ctx,
                                       [(data.rom_addresses[self.game_version]["gArchipelagoInfo"], 16, "ROM")]))[0]
        ctx.auth = base64.b64encode(auth_raw).decode("utf-8")

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.server.socket.closed or ctx.slot_data is None:
            return

        try:
            guards: Dict[str, Tuple[int, bytes, str]] = {}

            # Checks that the player is in the overworld
            guards["IN OVERWORLD"] = (
                data.ram_addresses[self.game_version]["gMain"] + 4,
                (data.ram_addresses[self.game_version]["CB2_Overworld"] + 1).to_bytes(4, "little"),
                "System Bus"
            )

            # Read save block addresses
            read_result = await bizhawk.read(
                ctx.bizhawk_ctx,
                [
                    (data.ram_addresses[self.game_version]["gSaveBlock1Ptr"], 4, "System Bus"),
                    (data.ram_addresses[self.game_version]["gSaveBlock2Ptr"], 4, "System Bus")
                ]
            )

            # Check that the save data hasn't moved
            guards["SAVE BLOCK 1"] = (data.ram_addresses[self.game_version]["gSaveBlock1Ptr"],
                                      read_result[0], "System Bus")
            guards["SAVE BLOCK 2"] = (data.ram_addresses[self.game_version]["gSaveBlock2Ptr"],
                                      read_result[1], "System Bus")

            sb1_address = int.from_bytes(guards["SAVE BLOCK 1"][1], "little")
            sb2_address = int.from_bytes(guards["SAVE BLOCK 2"][1], "little")

            await self.handle_received_items(ctx, guards)

            # Read flags in 2 chunks
            read_result = await bizhawk.guarded_read(
                ctx.bizhawk_ctx,
                [(sb1_address + 0x1090, 0x90, "System Bus")],  # Flags
                [guards["IN OVERWORLD"], guards["SAVE BLOCK 1"]]
            )

            if read_result is None:  # Not in overworld or save block moved
                return

            flag_bytes = read_result[0]

            read_result = await bizhawk.guarded_read(
                ctx.bizhawk_ctx,
                [(sb1_address + 0x1120, 0x90, "System Bus")],  # Flags continued
                [guards["IN OVERWORLD"], guards["SAVE BLOCK 1"]]
            )

            if read_result is not None:
                flag_bytes += read_result[0]

            read_result = await bizhawk.guarded_read(
                ctx.bizhawk_ctx,
                [(sb2_address + 0x018 + 0x10, 0x34, "System Bus")],  # Caught Pokemon
                [guards["IN OVERWORLD"], guards["SAVE BLOCK 2"]]
            )

            if read_result is None:  # Not in overworld or save block moved
                return

            pokemon_caught_bytes = read_result[0]

            game_clear = False
            local_set_events = {flag_name: False for flag_name in TRACKER_EVENT_FLAGS}
            local_checked_locations = set()
            caught_pokemon = 0

            # Check set flags
            for byte_i, byte in enumerate(flag_bytes):
                for i in range(8):
                    if byte & (1 << i) != 0:
                        flag_id = byte_i * 8 + i

                        location_id = offset_flag(flag_id)
                        if location_id in ctx.server_locations:
                            local_checked_locations.add(location_id)

                        for j in DEFEATED_CHAMPION_FLAGS:
                            if flag_id == j:
                                game_clear = True

                        if flag_id == data.constants["FLAG_DEFEATED_CHAMP"]:
                            game_clear = True

                        if flag_id in EVENT_FLAG_MAP:
                            local_set_events[EVENT_FLAG_MAP[flag_id]] = True

            # Get caught pokemon count
            for byte_i, byte in enumerate(pokemon_caught_bytes):
                for i in range(8):
                    if byte & (1 << i) != 0:
                        caught_pokemon += 1

            # Send locations
            if local_checked_locations != self.local_checked_locations:
                self.local_checked_locations = local_checked_locations

                if local_checked_locations is not None:
                    await ctx.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": list(local_checked_locations)
                    }])

            # Send game clear
            if not ctx.finished_game and game_clear:
                await ctx.send_msgs([{
                    "cmd": "StatusUpdate",
                    "status": ClientStatus.CLIENT_GOAL,
                }])

            # Send tracker event flags
            if local_set_events != self.local_set_events and ctx.slot is not None:
                event_bitfield = 0
                for i, flag_name in enumerate(TRACKER_EVENT_FLAGS):
                    if local_set_events[flag_name]:
                        event_bitfield |= 1 << i

                await ctx.send_msgs([{
                    "cmd": "Set",
                    "key": f"pokemon_frlg_events_{ctx.team}_{ctx.slot}",
                    "default": 0,
                    "want_reply": False,
                    "operations": [{"operation": "or", "value": event_bitfield}],
                }])
                self.local_set_events = local_set_events

            # Send caught pokemon amount
            if caught_pokemon != self.caught_pokemon and ctx.slot is not None:
                await ctx.send_msgs([{
                    "cmd": "Set",
                    "key": f"pokemon_frlg_pokedex_{ctx.team}_{ctx.slot}",
                    "default": 0,
                    "want_reply": False,
                    "operations": [{"operation": "replace", "value": caught_pokemon},]
                }])
                self.caught_pokemon = caught_pokemon

        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect
            pass

    async def handle_received_items(self, ctx: "BizHawkClientContext",
                                    guards: Dict[str, Tuple[int, bytes, str]]) -> None:
        """
        Checks the index of the most recently received item and whether the item queue is full. Writes the next item
        into the game if necessary.
        """
        received_item_address = data.ram_addresses[self.game_version]["gArchipelagoReceivedItem"]

        sb1_address = int.from_bytes(guards["SAVE BLOCK 1"][1], "little")

        read_result = await bizhawk.guarded_read(
            ctx.bizhawk_ctx,
            [
                (sb1_address + 0x3D88, 2, "System Bus"),
                (received_item_address + 4, 1, "System Bus")
            ],
            [guards["IN OVERWORLD"], guards["SAVE BLOCK 1"]]
        )
        if read_result is None:  # Not in overworld or save block moved
            return

        num_received_items = int.from_bytes(read_result[0], "little")
        received_item_is_empty = read_result[1][0] == 0

        if num_received_items < len(ctx.items_received) and received_item_is_empty:
            next_item = ctx.items_received[num_received_items]
            should_display = 1 if next_item.flags & 1 or next_item.player == ctx.slot else 0
            await bizhawk.write(ctx.bizhawk_ctx, [
                (received_item_address, reverse_offset_item_value(next_item.item).to_bytes(2, "little"), "System Bus"),
                (received_item_address + 2, (num_received_items + 1).to_bytes(2, "little"), "System Bus"),
                (received_item_address + 4, [1], "System Bus"),
                (received_item_address + 5, [should_display], "System Bus")
            ])
