# -*- coding: utf-8 -*-
from typing import Union


class EventBase(object):
    player_id = 0
    type = ''
    discard_tile = None  # type: Optional[int]
    meld_tiles = None  # type: Optional[List[int]]

    @property
    def is_agari(self) -> bool:
        return self.type == 'tsumo' or self.type == 'ron' or self.type == 'chan_kan'


class DiscardEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int):
        self.player_id = player_id
        self.type = 'discard'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class RiichiEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int):
        self.player_id = player_id
        self.type = 'riichi'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class PonEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_id = player_id
        self.type = 'pon'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class ChiEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_id = player_id
        self.type = 'chi'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class AnKanEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_id = player_id
        self.type = 'an_kan'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class MinKanEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_id = player_id
        self.type = 'min_kan'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class KaKanEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_id = player_id
        self.type = 'ka_kan'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class TsumoEvent(EventBase):
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.type = 'tsumo'
        self.discard_tile = None
        self.meld_tiles = None


class RonEvent(EventBase):
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.type = 'ron'
        self.discard_tile = None
        self.meld_tiles = None


class ChanKanEvent(EventBase):
    def __init__(self, player_id: int, discard_tile: int):
        self.player_id = player_id
        self.type = 'chan_kan'
        self.discard_tile = None
        self.meld_tiles = None


class KyushuKyuhaiEvent(EventBase):
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.type = 'kyushu_kyuhai'
        self.discard_tile = None
        self.meld_tiles = None


class NoneEvent(EventBase):
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.type = 'none'
        self.discard_tile = None
        self.meld_tiles = None


MeldEvent = Union[
    PonEvent,
    ChiEvent,
    AnKanEvent,
    MinKanEvent,
    KaKanEvent,
]

AgariEvent = Union[
    TsumoEvent,
    RonEvent,
    ChanKanEvent,
]

Event = Union[
    DiscardEvent,
    RiichiEvent,
    MeldEvent,
    AgariEvent,
    KyushuKyuhaiEvent,
    NoneEvent,
]
