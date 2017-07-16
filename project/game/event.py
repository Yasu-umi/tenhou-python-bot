# -*- coding: utf-8 -*-
from typing import Union, Optional, Union, List, Tuple


class EventBase(object):
    player_id = 0
    type = ''
    discard_tile:  Optional[int] = None
    # first tile is called tile
    meld_tiles: Union[None, Tuple[int, int, int], Tuple[int, int, int, int]] = None
    opened: Optional[bool] = None

    @property
    def is_agari(self) -> bool:
        return isinstance(self, TsumoAgariEvent) or isinstance(self, RonAgariEvent) or isinstance(self, ChanKanAgariEvent)

    def __str__(self) -> str:
        return "player_id: {}, type: {}, discard_tile: {}, meld_tiles: {}".format(
            self.player_id, self.type, self.discard_tile, self.meld_tiles
        )


class TsumoEvent(EventBase):
    discard_tile: int
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'tsumo'
        self.discard_tile = discard_tile


class RinshanTsumoEvent(EventBase):
    discard_tile: int
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'rinshan_tsumo'
        self.discard_tile = discard_tile


class RiichiEvent(EventBase):
    discard_tile: int
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'riichi'
        self.discard_tile = discard_tile


class PonEvent(EventBase):
    discard_tile: int
    meld_tiles: Tuple[int, int, int]
    opened: bool

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int], opened: bool) -> None:
        self.player_id = player_id
        self.type = 'pon'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles
        self.opened = opened


class ChiEvent(EventBase):
    discard_tile: int
    meld_tiles: Tuple[int, int, int]
    opened: bool

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int], opened: bool) -> None:
        self.player_id = player_id
        self.type = 'chi'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles
        self.opened = opened


class AnKanDeclarationEvent(EventBase):
    discard_tile: int
    meld_tiles: Tuple[int, int, int, int]
    opened: bool = False

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'an_kan_declaration'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class MinKanDeclarationEvent(EventBase):
    discard_tile: int
    meld_tiles: Tuple[int, int, int, int]
    opened: bool = True

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'min_kan_declaration'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class KaKanDeclarationEvent(EventBase):
    discard_tile: int
    meld_tiles: Tuple[int, int, int, int]
    opened: bool = True

    def __init__(self, player_id: int, discard_tile: int, meld_tiles: Tuple[int, int, int, int]) -> None:
        self.player_id = player_id
        self.type = 'ka_kan_declaration'
        self.discard_tile = discard_tile
        self.meld_tiles = meld_tiles


class TsumoAgariEvent(EventBase):
    discard_tile: None = None
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'tsumo_agari'


class RonAgariEvent(EventBase):
    discard_tile: None = None
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'ron_agari'


class ChanKanAgariEvent(EventBase):
    discard_tile: None = None
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int, discard_tile: int) -> None:
        self.player_id = player_id
        self.type = 'chan_kan_agari'


class KyushuKyuhaiEvent(EventBase):
    discard_tile: None = None
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'kyushu_kyuhai'


class NoneEvent(EventBase):
    discard_tile: None = None
    meld_tiles: None = None
    opened: None = None

    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.type = 'none'


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
