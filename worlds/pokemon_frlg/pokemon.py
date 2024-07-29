import math
from typing import TYPE_CHECKING, Dict, List, Set, Tuple

from .data import (data, LEGENDARY_POKEMON, NUM_REAL_SPECIES, EncounterSpeciesData, EventData, LearnsetMove,
                   SpeciesData, TrainerPokemonData)
from .options import (GameVersion, HmCompatibility, RandomizeAbilities, RandomizeLegendaryPokemon, RandomizeMiscPokemon,
                      RandomizeMoves, RandomizeStarters, RandomizeTrainerParties, RandomizeTypes, RandomizeWildPokemon,
                      TmTutorCompatibility, WildPokemonGroups)
from .util import bool_array_to_int, int_to_bool_array

if TYPE_CHECKING:
    from random import Random
    from . import PokemonFRLGWorld

_DAMAGING_MOVES = frozenset({
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 13, 16, 17, 20, 21, 22, 23, 24, 25,
    26, 27, 29, 30, 31, 33, 34, 35, 36, 37,
    38, 40, 41, 42, 44, 49, 51, 52, 53, 55,
    56, 58, 59, 60, 61, 62, 63, 64, 65, 66,
    67, 69, 71, 72, 75, 76, 80, 82, 83, 84,
    85, 87, 88, 89, 91, 93, 94, 98, 99, 101,
    121, 122, 123, 124, 125, 126, 128, 129, 130, 131,
    132, 136, 140, 141, 143, 145, 146, 149, 152, 154,
    155, 157, 158, 161, 162, 163, 167, 168, 172, 175,
    177, 179, 181, 183, 185, 188, 189, 190, 192, 196,
    198, 200, 202, 205, 209, 210, 211, 216, 217, 218,
    221, 222, 223, 224, 225, 228, 229, 231, 232, 233,
    237, 238, 239, 242, 245, 246, 247, 248, 250, 251,
    253, 257, 263, 265, 267, 276, 279, 280, 282, 284,
    290, 292, 295, 296, 299, 301, 302, 304, 305, 306,
    307, 308, 309, 310, 311, 314, 315, 317, 318, 323,
    324, 325, 326, 327, 328, 330, 331, 332, 333, 337,
    338, 340, 341, 342, 343, 344, 345, 348, 350, 351,
    352, 353, 354
})

_HM_MOVES = frozenset({
    15, 19, 57, 70, 127, 148, 249, 291
})

_MOVE_BLACKLIST = frozenset({
    0,
    165
})

_DUNGEON_GROUPS: Dict[str, str] = {
    "MAP_MT_MOON_1F": "MAP_MT_MOON",
    "MAP_MT_MOON_B1F": "MAP_MT_MOON",
    "MAP_MT_MOON_B2F": "MAP_MT_MOON",
    "MAP_ROCK_TUNNEL_1F": "MAP_ROCK_TUNNEL",
    "MAP_ROCK_TUNNEL_B1F": "MAP_ROCK_TUNNEL",
    "MAP_POKEMON_TOWER_3F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_4F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_5F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_6F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_7F": "MAP_POKEMON_TOWER",
    "MAP_SAFARI_ZONE_CENTER": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_EAST": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_NORTH": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_WEST": "MAP_SAFARI_ZONE",
    "MAP_SEAFOAM_ISLANDS_1F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B1F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B2F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B3F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B4F": "MAP_SEAFOAM_ISLANDS",
    "MAP_POKEMON_MANSION_1F": "MAP_POKEMON_MANSION",
    "MAP_POKEMON_MANSION_2F": "MAP_POKEMON_MANSION",
    "MAP_POKEMON_MANSION_3F": "MAP_POKEMON_MANSION",
    "MAP_POKEMON_MANSION_B1F": "MAP_POKEMON_MANSION",
    "MAP_VICTORY_ROAD_1F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_2F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_3F": "MAP_VICTORY_ROAD",
    "MAP_MT_EMBER_EXTERIOR": "MAP_MT_EMBER",
    "MAP_MT_EMBER_SUMMIT_PATH_1F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_SUMMIT_PATH_2F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_SUMMIT_PATH_3F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_1F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B1F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B1F_STAIRS": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B2F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B2F_STAIRS": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B3F": "MAP_MT_EMBER",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_ENTRANCE": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_1F": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_B1F": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_BACK": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM1": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM2": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM3": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM4": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM5": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM6": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM7": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM8": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM9": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM10": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM11": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM12": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM13": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM14": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_CERULEAN_CAVE_1F": "MAP_CERULEAN_CAVE",
    "MAP_CERULEAN_CAVE_2F": "MAP_CERULEAN_CAVE",
    "MAP_CERULEAN_CAVE_B1F": "MAP_CERULEAN_CAVE"
}

STARTER_INDEX: Dict[str, int] = {
    "STARTER_POKEMON_BULBASAUR": 0,
    "STARTER_POKEMON_SQUIRTLE": 1,
    "STARTER_POKEMON_CHARMANDER": 2,
}

_NON_STATIC_MISC_POKEMON: List[str] = {
    "CELADON_PRIZE_POKEMON_1",
    "CELADON_PRIZE_POKEMON_2",
    "CELADON_PRIZE_POKEMON_3",
    "CELADON_PRIZE_POKEMON_4",
    "CELADON_PRIZE_POKEMON_5"
}

# The tuple represnts (trainer name, starter index in party, starter evolution stage)
_RIVAL_STARTER_POKEMON: List[Tuple[str, int, int]] = [
    [
        ("TRAINER_RIVAL_OAKS_LAB_BULBASAUR", 0, 0),
        ("TRAINER_RIVAL_ROUTE22_EARLY_BULBASAUR", 1, 0),
        ("TRAINER_RIVAL_CERULEAN_BULBASAUR", 3, 0),
        ("TRAINER_RIVAL_SS_ANNE_BULBASAUR", 3, 1),
        ("TRAINER_RIVAL_POKEMON_TOWER_BULBASAUR", 4, 1),
        ("TRAINER_RIVAL_SILPH_BULBASAUR", 4, 2),
        ("TRAINER_RIVAL_ROUTE22_LATE_BULBASAUR", 5, 2),
        ("TRAINER_CHAMPION_FIRST_BULBASAUR", 5, 2),
        ("TRAINER_CHAMPION_REMATCH_BULBASAUR", 5, 2),
    ],
    [
        ("TRAINER_RIVAL_OAKS_LAB_CHARMANDER", 0, 0),
        ("TRAINER_RIVAL_ROUTE22_EARLY_CHARMANDER", 1, 0),
        ("TRAINER_RIVAL_CERULEAN_CHARMANDER", 3, 0),
        ("TRAINER_RIVAL_SS_ANNE_CHARMANDER", 3, 1),
        ("TRAINER_RIVAL_POKEMON_TOWER_CHARMANDER", 4, 1),
        ("TRAINER_RIVAL_SILPH_CHARMANDER", 4, 2),
        ("TRAINER_RIVAL_ROUTE22_LATE_CHARMANDER", 5, 2),
        ("TRAINER_CHAMPION_FIRST_CHARMANDER", 5, 2),
        ("TRAINER_CHAMPION_REMATCH_CHARMANDER", 5, 2),
    ],
    [
        ("TRAINER_RIVAL_OAKS_LAB_SQUIRTLE", 0, 0),
        ("TRAINER_RIVAL_ROUTE22_EARLY_SQUIRTLE", 1, 0),
        ("TRAINER_RIVAL_CERULEAN_SQUIRTLE", 3, 0),
        ("TRAINER_RIVAL_SS_ANNE_SQUIRTLE", 3, 1),
        ("TRAINER_RIVAL_POKEMON_TOWER_SQUIRTLE", 4, 1),
        ("TRAINER_RIVAL_SILPH_SQUIRTLE", 4, 2),
        ("TRAINER_RIVAL_ROUTE22_LATE_SQUIRTLE", 5, 2),
        ("TRAINER_CHAMPION_FIRST_SQUIRTLE", 5, 2),
        ("TRAINER_CHAMPION_REMATCH_SQUIRTLE", 5, 2)
    ]
]


def _get_random_type(random: "Random") -> int:
    picked_type = random.randrange(0, 18)
    while picked_type == 9:  # Don't pick the ??? type
        picked_type = random.randrange(0, 18)

    return picked_type


def _get_random_move(random: "Random", blacklist: Set[int]) -> int:
    extended_blacklist = _HM_MOVES | _MOVE_BLACKLIST | blacklist
    allowed_moves = [i for i in range(data.constants["MOVES_COUNT"]) if i not in extended_blacklist]
    return random.choice(allowed_moves)


def _get_random_damaging_move(random: "Random", blacklist: Set[int]) -> int:
    allowed_moves = [i for i in list(_DAMAGING_MOVES) if i not in blacklist]
    return random.choice(allowed_moves)


def _filter_species_by_nearby_bst(species: List[SpeciesData], target_bst: int) -> List[SpeciesData]:
    # Sort by difference in bst, then chop off the tail of the list that's more than
    # 10% different. If that leaves the list empty, increase threshold to 20%, then 30%, etc.
    species = sorted(species, key=lambda species: abs(sum(species.base_stats) - target_bst))
    cutoff_index = 0
    max_percent_different = 10
    while cutoff_index == 0 and max_percent_different < 10000:
        while (cutoff_index < len(species) and
               abs(sum(species[cutoff_index].base_stats) - target_bst) < target_bst * (max_percent_different / 100)):
            cutoff_index += 1
        max_percent_different += 10

    return species[:cutoff_index + 1]


def _get_trainer_pokemon_moves(world: "PokemonFRLGWorld",
                               species: SpeciesData,
                               pokemon: TrainerPokemonData) -> Tuple[int, int, int, int]:
    if species.species_id not in world.per_species_tmhm_moves:
        world.per_species_tmhm_moves[species.species_id] = sorted({
            data.tmhm_moves[i]
            for i, is_compatible in enumerate(int_to_bool_array(species.tm_hm_compatibility))
            if is_compatible
        })

    # TMs and HMs compatible with the species
    tm_hm_movepool = world.per_species_tmhm_moves[species.species_id]

    # Moves the Pokémon could have learned by now
    level_up_movepool = sorted({
        move.move_id
        for move in species.learnset
        if move.move_id != 0 and move.level <= pokemon.level
    })

    if len(level_up_movepool) < 4:
        level_up_moves = [level_up_movepool[i]
                          if i < len(level_up_movepool) else 0 for i in range(4)]
    else:
        level_up_moves = world.random.sample(level_up_movepool, 4)

    if len(tm_hm_movepool) < 4:
        tm_hm_moves = list(reversed(list(tm_hm_movepool[i]
                                         if i < len(tm_hm_movepool) else 0 for i in range(4))))
    else:
        tm_hm_moves = world.random.sample(tm_hm_movepool, 4)

    # 25% chance to pick a move from TMs or HMs
    new_moves = (
        tm_hm_moves[0] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[0],
        tm_hm_moves[1] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[1],
        tm_hm_moves[2] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[2],
        tm_hm_moves[3] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[3]
    )

    return new_moves


def randomize_types(world: "PokemonFRLGWorld") -> None:
    if world.options.types == RandomizeTypes.option_shuffle:
        type_map = list(range(18))
        world.random.shuffle(type_map)

        # Map the ??? type to itself. No Pokémon have this type, and we don't want any Pokémon to have it.
        mystery_type_index = type_map.index(9)
        type_map[mystery_type_index], type_map[9] = type_map[9], type_map[mystery_type_index]

        for species in world.modified_species.values():
            species.types = (type_map[species.types[0]], type_map[species.types[1]])
    elif world.options.types == RandomizeTypes.option_completely_random:
        for species in world.modified_species.values():
            new_type_1 = _get_random_type(world.random)
            new_type_2 = new_type_1

            if species.types[0] != species.types[1]:
                while new_type_1 == new_type_2:
                    new_type_2 = _get_random_type(world.random)

            species.types = (new_type_1, new_type_2)
    elif world.options.types == RandomizeTypes.option_follow_evolutions:
        already_randomized = set()

        for species in world.modified_species.values():
            if species.species_id in already_randomized:
                continue
            elif species.pre_evolution is not None:
                continue

            type_map = list(range(18))
            world.random.shuffle(type_map)

            # Map the ??? type to itself. No Pokémon have this type, and we don't want any Pokémon to have it.
            mystery_type_index = type_map.index(9)
            type_map[mystery_type_index], type_map[9] = type_map[9], type_map[mystery_type_index]

            evolutions = [species]
            while len(evolutions) > 0:
                evolution = evolutions.pop()
                evolution.types = (type_map[evolution.types[0]], type_map[evolution.types[1]])
                already_randomized.add(evolution.species_id)
                evolutions += [world.modified_species[evo.species_id] for evo in evolution.evolutions]


def randomize_abilities(world: "PokemonFRLGWorld") -> None:
    if world.options.abilities == RandomizeAbilities.option_vanilla:
        return

    allowed_abilities = list(range(data.constants["ABILITIES_COUNT"]))
    allowed_abilities.remove(data.constants["ABILITY_NONE"])
    allowed_abilities.remove(data.constants["ABILITY_CACOPHONY"])
    for ability_id in world.blacklisted_abilities:
        allowed_abilities.remove(ability_id)

    if world.options.abilities == RandomizeAbilities.option_follow_evolutions:
        already_randomized = set()

        for species in world.modified_species.values():
            if species.species_id in already_randomized:
                continue
            elif (species.pre_evolution is not None and
                  species.abilities == data.species[species.pre_evolution].abilities):
                continue

            old_abilities = species.abilities
            new_abilities = (
                0 if old_abilities[0] == 0 else world.random.choice(allowed_abilities),
                0 if old_abilities[1] == 0 else world.random.choice(allowed_abilities)
            )

            evolutions = [species]
            while len(evolutions) > 0:
                evolution = evolutions.pop()
                if evolution.abilities == old_abilities:
                    evolution.abilities = new_abilities
                    already_randomized.add(evolution.species_id)
                    evolutions += [world.modified_species[evo.species_id] for evo in evolution.evolutions]
    else:
        for species in world.modified_species.values():
            old_abilities = species.abilities
            new_abilities = (
                0 if old_abilities[0] == 0 else world.random.choice(allowed_abilities),
                0 if old_abilities[1] == 0 else world.random.choice(allowed_abilities)
            )
            species.abilities = new_abilities


def randomize_moves(world: "PokemonFRLGWorld") -> None:
    if world.options.moves == RandomizeMoves.option_vanilla:
        return

    for species in world.modified_species.values():
        old_learnset = species.learnset
        new_learnset: List[LearnsetMove] = []

        # All species have 4 moves at level 0. Up to 3 of them can be MOVE_NONE and
        # are used for the start with 4 moves option. We need to either replace them
        # with actual moves or leave them alone depending on the option.
        move_index = 0
        while old_learnset[move_index].move_id == 0:
            if world.options.moves == RandomizeMoves.option_start_with_four_moves:
                new_move = _get_random_move(world.random,
                                            {move.move_id for move in new_learnset} | world.blacklist_moves)
            else:
                new_move = 0
            new_learnset.append(LearnsetMove(old_learnset[move_index].level, new_move))
            move_index += 1

        while move_index < len(old_learnset):
            if move_index == 3:
                new_move = _get_random_damaging_move(world.random, {move.move_id for move in new_learnset})
            else:
                new_move = _get_random_move(world.random,
                                            {move.move_id for move in new_learnset} | world.blacklist_moves)
            new_learnset.append(LearnsetMove(old_learnset[move_index].level, new_move))
            move_index += 1

        species.learnset = new_learnset


def randomize_wild_encounters(world: "PokemonFRLGWorld") -> None:
    if world.options.wild_pokemon == RandomizeWildPokemon.option_vanilla:
        return

    from collections import defaultdict

    game_version = world.options.game_version.current_key
    min_pokemon_needed = math.ceil(max(world.options.oaks_aide_route_2.value,
                                       world.options.oaks_aide_route_10.value,
                                       world.options.oaks_aide_route_11.value,
                                       world.options.oaks_aide_route_16.value,
                                       world.options.oaks_aide_route_15.value) * 1.2)
    should_match_bst = world.options.wild_pokemon in {
        RandomizeWildPokemon.option_match_base_stats,
        RandomizeWildPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.wild_pokemon in {
        RandomizeWildPokemon.option_match_type,
        RandomizeWildPokemon.option_match_base_stats_and_type
    }
    species_map: Dict[int, int] = {}
    dungeon_species_map: Dict[str, Dict[int, int]] = {}

    for map_group in _DUNGEON_GROUPS.values():
        if map_group not in dungeon_species_map:
            dungeon_species_map[map_group] = {}

    # Route 21 is split into a North and South Map. We'll set this after we randomize one of them
    # in order to ensure that both maps have the same encounters
    route_21_randomized = False

    placed_species = set()

    map_names = list(world.modified_maps.keys())
    world.random.shuffle(map_names)
    for map_name in map_names:
        map_data = world.modified_maps[map_name]

        new_encounter_slots: List[List[int]] = [None, None, None]
        old_encounters = [map_data.land_encounters,
                          map_data.water_encounters,
                          map_data.fishing_encounters]

        # Check if the current map is a Route 21 map and the other one has already been randomized.
        # If so, set the encounters of the current map based on the other Route 21 map.
        if map_name == "MAP_ROUTE21_NORTH" and route_21_randomized:
            map_data.land_encounters.slots[game_version] = \
                world.modified_maps["MAP_ROUTE21_SOUTH"].land_encounters.slots[game_version]
            map_data.water_encounters.slots[game_version] = \
                world.modified_maps["MAP_ROUTE21_SOUTH"].water_encounters.slots[game_version]
            map_data.fishing_encounters.slots[game_version] = \
                world.modified_maps["MAP_ROUTE21_SOUTH"].fishing_encounters.slots[game_version]
            continue
        elif map_name == "MAP_ROUTE21_SOUTH" and route_21_randomized:
            map_data.land_encounters.slots[game_version] = \
                world.modified_maps["MAP_ROUTE21_NORTH"].land_encounters.slots[game_version]
            map_data.water_encounters.slots[game_version] = \
                world.modified_maps["MAP_ROUTE21_NORTH"].water_encounters.slots[game_version]
            map_data.fishing_encounters.slots[game_version] = \
                world.modified_maps["MAP_ROUTE21_NORTH"].fishing_encounters.slots[game_version]
            continue

        if map_name == "MAP_ROUTE21_NORTH" or map_name == "MAP_ROUTE21_SOUTH":
            route_21_randomized = True

        for i, table in enumerate(old_encounters):
            if table is not None:
                # Create a map from the original species to new species
                # instead of just randomizing every slot.
                # Force area 1-to-1 mapping, in other words.
                species_old_to_new_map: Dict[int, int] = {}
                for species_data in table.slots[game_version]:
                    species_id = species_data.species_id
                    if species_id not in species_old_to_new_map:
                        if (world.options.wild_pokemon_groups == WildPokemonGroups.option_species and
                                species_id in species_map):
                            new_species_id = species_map[species_id]
                        elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                              map_name in _DUNGEON_GROUPS and
                              species_id in dungeon_species_map[_DUNGEON_GROUPS[map_name]]):
                            new_species_id = dungeon_species_map[_DUNGEON_GROUPS[map_name]][species_id]
                        else:
                            original_species = data.species[species_id]

                            # Construct progressive tiers of blacklists that can be peeled back if they
                            # collectively cover too much of the Pokédex. A lower index in `blacklists`
                            # indicates a more important set of species to avoid. Entries at `0` will
                            # always be blacklisted.
                            blacklists: Dict[int, List[Set[int]]] = defaultdict(list)

                            # Blacklist Pokémon already on this table
                            blacklists[0].append(set(species_old_to_new_map.values()))

                            # If we are randomizing by groups, blacklist any species that is
                            # already a part of this group
                            if world.options.wild_pokemon_groups == WildPokemonGroups.option_species:
                                blacklists[0].append(set(species_map.values()))
                            elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                                  map_name in _DUNGEON_GROUPS):
                                blacklists[0].append(set(dungeon_species_map[_DUNGEON_GROUPS[map_name]].values()))

                            # If we haven't placed enough species for Oak's Aides yet, blacklist
                            # species that have already been placed until we reach that number
                            if len(placed_species) < min_pokemon_needed:
                                blacklists[1].append(placed_species)

                            # Blacklist from player's options
                            blacklists[2].append(world.blacklisted_wild_pokemon)

                            # Type matching blacklist
                            if should_match_type:
                                blacklists[3].append({
                                    species.species_id
                                    for species in world.modified_species.values()
                                    if not bool(set(species.types) & set(original_species.types))
                                })

                            merged_blacklist: Set[int] = set()
                            for max_priority in reversed(sorted(blacklists.keys())):
                                merged_blacklist = set()
                                for priority in blacklists.keys():
                                    if priority <= max_priority:
                                        for blacklist in blacklists[priority]:
                                            merged_blacklist |= blacklist

                                if len(merged_blacklist) < NUM_REAL_SPECIES:
                                    break

                            candidates = [
                                species for species in world.modified_species.values() if
                                species.species_id not in merged_blacklist
                            ]

                            if should_match_bst:
                                candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

                            new_species_id = world.random.choice(candidates).species_id

                            if world.options.wild_pokemon_groups == WildPokemonGroups.option_species:
                                species_map[original_species.species_id] = new_species_id
                            elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                                  map_name in _DUNGEON_GROUPS):
                                dungeon_species_map[_DUNGEON_GROUPS[map_name]][original_species.species_id] = \
                                    new_species_id

                        species_old_to_new_map[species_id] = new_species_id
                        placed_species.add(new_species_id)

                # Actually create the new list of slots and encounter table
                new_slots: List[EncounterSpeciesData] = []
                for species_data in table.slots[game_version]:
                    new_slots.append(EncounterSpeciesData(
                        species_old_to_new_map[species_data.species_id],
                        species_data.min_level,
                        species_data.max_level
                    ))

                new_encounter_slots[i] = new_slots

        if map_data.land_encounters is not None:
            map_data.land_encounters.slots[game_version] = new_encounter_slots[0]
        if map_data.water_encounters is not None:
            map_data.water_encounters.slots[game_version] = new_encounter_slots[1]
        if map_data.fishing_encounters is not None:
            map_data.fishing_encounters.slots[game_version] = new_encounter_slots[2]


def randomize_starters(world: "PokemonFRLGWorld") -> None:
    if world.options.starters == RandomizeStarters.option_vanilla:
        return

    should_match_bst = world.options.starters in {
        RandomizeStarters.option_match_base_stats,
        RandomizeStarters.option_match_base_stats_and_type,
    }
    should_match_type = world.options.starters in {
        RandomizeStarters.option_match_type,
        RandomizeStarters.option_match_base_stats_and_type,
    }

    new_starters: List[SpeciesData] = []

    for name, starter in world.modified_starters.items():
        original_starter = data.species[starter.species_id]

        type_blacklist = {
            species.species_id
            for species in world.modified_species.values()
            if not bool(set(species.types) & set(original_starter.types))
        } if should_match_type else set()

        merged_blacklist = set(s.species_id for s in new_starters) | world.blacklisted_starters | type_blacklist
        if len(merged_blacklist) == NUM_REAL_SPECIES:
            merged_blacklist = set(s.species_id for s in new_starters) | world.blacklisted_starters
        if len(merged_blacklist) == NUM_REAL_SPECIES:
            merged_blacklist = set(s.species_id for s in new_starters)

        candidates = [
            species
            for species in world.modified_species.values()
            if species.species_id not in merged_blacklist
        ]

        if should_match_bst:
            candidates = _filter_species_by_nearby_bst(candidates, sum(original_starter.base_stats))

        new_starter = world.random.choice(candidates)
        starter.species_id = new_starter.species_id
        new_starters.append(new_starter)

    # Change the starter in your rival's party
    for i, starter_data in enumerate(new_starters):
        starter_stages: List[SpeciesData] = [starter_data, None, None]
        if len(starter_stages[0].evolutions) > 0:
            evolution = world.random.choice(starter_stages[0].evolutions)
            starter_stages[1] = world.modified_species[evolution.species_id]
            if len(starter_stages[1].evolutions) > 0:
                evolution = world.random.choice(starter_stages[1].evolutions)
                starter_stages[2] = world.modified_species[evolution.species_id]
            else:
                starter_stages[2] = starter_stages[1]
        else:
            starter_stages[1] = starter_stages[0]
            starter_stages[2] = starter_stages[0]

        for trainer_name, starter_index, evolution_stage in _RIVAL_STARTER_POKEMON[i]:
            trainer_data = world.modified_trainers[data.constants[trainer_name]]
            starter_species = starter_stages[evolution_stage]
            rival_starter = trainer_data.party.pokemon[starter_index]
            new_moves = _get_trainer_pokemon_moves(world, starter_species, rival_starter)
            trainer_data.party.pokemon[starter_index] = TrainerPokemonData(starter_species.species_id,
                                                                           rival_starter.level,
                                                                           new_moves,
                                                                           True)


def randomize_legendaries(world: "PokemonFRLGWorld") -> None:
    if world.options.legendary_pokemon == RandomizeLegendaryPokemon.option_vanilla:
        return

    game_version = world.options.game_version.current_key

    should_match_bst = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_base_stats,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_type,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }

    placed_species = set()

    for name, legendary in data.legendary_pokemon.items():
        original_species = world.modified_species[legendary.species_id[game_version]]

        if world.options.legendary_pokemon == RandomizeLegendaryPokemon.option_legendaries:
            candidates = [species for species in world.modified_species.values() if
                          species.species_id in LEGENDARY_POKEMON and species.species_id not in placed_species]
        else:
            candidates = list(world.modified_species.values())
        if should_match_type:
            candidates = [
                species
                for species in candidates
                if bool(set(species.types) & set(original_species.types))
            ]
        if should_match_bst:
            candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

        new_species_id = world.random.choice(candidates).species_id
        world.modified_legendary_pokemon[name].species_id[game_version] = new_species_id
        placed_species.add(new_species_id)

    # Update the events that correspond to the legendary Pokémon
    for name, legendary_pokemon in world.modified_legendary_pokemon.items():
        if name not in world.modified_events:
            continue

        species = world.modified_species[legendary_pokemon.species_id[game_version]]
        item_name = data.events[name].item.split()

        if item_name[0] == "Static":
            item = f"Static {species.name}"
        elif item_name[0] == "Missable":
            item = f"Missable {species.name}"
        else:
            item = item_name[0]

        new_event = EventData(
            world.modified_events[name].id,
            world.modified_events[name].name,
            item,
            world.modified_events[name].parent_region_id,
            world.modified_events[name].tags
        )

        world.modified_events[name] = new_event


def randomize_misc_pokemon(world: "PokemonFRLGWorld") -> None:
    if world.options.misc_pokemon == RandomizeMiscPokemon.option_vanilla:
        return

    game_version = world.options.game_version.current_key

    should_match_bst = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_base_stats,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_type,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }

    for name, misc_pokemon in data.misc_pokemon.items():
        original_species = world.modified_species[misc_pokemon.species_id[game_version]]

        candidates = list(world.modified_species.values())
        if should_match_type:
            candidates = [
                species
                for species in candidates
                if bool(set(species.types) & set(original_species.types))
            ]
        if should_match_bst:
            candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

        world.modified_misc_pokemon[name].species_id[game_version] = world.random.choice(candidates).species_id

    # Update the events that correspond to the misc Pokémon
    for name, misc_pokemon in world.modified_misc_pokemon.items():
        if name not in world.modified_events:
            continue

        species = world.modified_species[misc_pokemon.species_id[game_version]]

        if type(data.events[name].item) is list:
            if game_version == GameVersion.option_firered:
                item_name = data.events[name].item[0].split()
            else:
                item_name = data.events[name].item[1].split()
        else:
            item_name = data.events[name].item.split()

        if item_name[0] == "Static":
            item = f"Static {species.name}"
        elif item_name[0] == "Missable":
            item = f"Missable {species.name}"
        else:
            item = item_name[0]

        new_event = EventData(
            world.modified_events[name].id,
            world.modified_events[name].name,
            item,
            world.modified_events[name].parent_region_id,
            world.modified_events[name].tags
        )

        world.modified_events[name] = new_event


def randomize_trainer_parties(world: "PokemonFRLGWorld") -> None:
    if world.options.trainers == RandomizeTrainerParties.option_vanilla:
        return

    should_match_bst = world.options.trainers in {
        RandomizeTrainerParties.option_match_base_stats,
        RandomizeTrainerParties.option_match_base_stats_and_type,
    }
    should_match_type = world.options.trainers in {
        RandomizeTrainerParties.option_match_type,
        RandomizeTrainerParties.option_match_base_stats_and_type,
    }

    for trainer_id, trainer in world.modified_trainers.items():
        for i, pokemon in enumerate(trainer.party.pokemon):
            if not pokemon.locked:
                original_species = data.species[pokemon.species_id]

                type_blacklist = {
                    species.species_id
                    for species in world.modified_species.values()
                    if not bool(set(species.types) & set(original_species.types))
                } if should_match_type else set()

                merged_blacklist = world.blacklisted_trainer_pokemon | type_blacklist
                if len(merged_blacklist) == NUM_REAL_SPECIES:
                    merged_blacklist = world.blacklisted_trainer_pokemon
                if len(merged_blacklist) == NUM_REAL_SPECIES:
                    merged_blacklist = set()

                candidates = [
                    species
                    for species in world.modified_species.values()
                    if species.species_id not in merged_blacklist
                ]

                if should_match_bst:
                    candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

                new_species = world.random.choice(candidates)

                new_moves = _get_trainer_pokemon_moves(world, new_species, pokemon)
                trainer.party.pokemon[i] = TrainerPokemonData(new_species.species_id,
                                                              pokemon.level,
                                                              new_moves,
                                                              False)


def randomize_tm_hm_compatability(world: "PokemonFRLGWorld") -> None:
    for species in world.modified_species.values():
        compatability_array = int_to_bool_array(species.tm_hm_compatibility)

        if world.options.tm_tutor_compatability != TmTutorCompatibility.special_range_names["vanilla"]:
            for i in range(0, 50):
                compatability_array[i] = world.random.random() < world.options.tm_tutor_compatability / 100

        if world.options.hm_compatability != HmCompatibility.special_range_names["vanilla"]:
            for i in range(50, 58):
                compatability_array[i] = world.random.random() < world.options.hm_compatability / 100

        species.tm_hm_compatibility = bool_array_to_int(compatability_array)
