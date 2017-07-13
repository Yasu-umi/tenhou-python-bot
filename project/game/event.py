# -*- coding: utf-8 -*-
from typing import Union, Optional, Union, List, Tuple


class EventBase(object):
    player_id = 0
    type = ''
    discard_tile:  Optional[int] = None
    meld_tiles: Union[None, Tuple[int, int, int], Tuple[int, int, int, int]] = None

    @property
    def is_agari(self) -> bool:
        return isinstance(self, TsumoAgariEvent) or isinstance(self, RonAgariEvent) or isinstance(self, ChanKanAgariEvent)

    def __str__(self) -> str:
        return "player_id: {}, type: {}, discard_tile: {}, meld_tiles: {}".format(
            self.player_id, self.type, self.discard_tile, self.meld_tiles
        )


class TsumoEvent(EventBase):
    discard_tile: int = -1

    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'tsumo'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class RinshanTsumoEvent(EventBase):
    discard_tile: int = -1

    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'rinshan_tsumo'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class RiichiEvent(EventBase):
    discard_tile: int

    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'riichi'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class PonEvent(EventBase):
    discard_tile: int

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'pon'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class ChiEvent(EventBase):
    discard_tile: int

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'chi'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class AnKanDeclarationEvent(EventBase):
    discard_tile: int

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'an_kan_declaration'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class MinKanDeclarationEvent(EventBase):
    discard_tile: int

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'min_kan_declaration'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class KaKanDeclarationEvent(EventBase):
    discard_tile: int

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'ka_kan_declaration'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class TsumoAgariEvent(EventBase):
    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'tsumo_agari'
        self.discard_tile = None
        self.meld_tiles = None


class RonAgariEvent(EventBase):
    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'ron_agari'
        self.discard_tile = None
        self.meld_tiles = None


class ChanKanAgariEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'chan_kan_agari'
        self.discard_tile = None
        self.meld_tiles = None


class KyushuKyuhaiEvent(EventBase):
    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'kyushu_kyuhai'
        self.discard_tile = None
        self.meld_tiles = None


class NoneEvent(EventBase):
    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'none'
        self.discard_tile = None
        self.meld_tiles = None


KanDeclarationEvent = Union[
    AnKanDeclarationEvent,
    MinKanDeclarationEvent,
    KaKanDeclarationEvent,
]

MeldEvent = Union[
    PonEvent,
    ChiEvent,
]

HasDiscardTileEvent = Union[
    MeldEvent,
    TsumoEvent,
    RinshanTsumoEvent,
    RiichiEvent,
]

AgariEvent = Union[
    TsumoAgariEvent,
    RonAgariEvent,
    ChanKanAgariEvent,
]

Event = Union[
    HasDiscardTileEvent,
    AgariEvent,
    KyushuKyuhaiEvent,
    NoneEvent,
]
