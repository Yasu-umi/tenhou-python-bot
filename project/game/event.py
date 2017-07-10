# -*- coding: utf-8 -*-
from typing import Union


class DiscardEvent(object):
    def __init__(self, player_seat: int, discard_tile: int):
        self.player_seat = player_seat
class EventBase(object):
    player_id = 0
    type = ''
    discard_tile = None  # type: Optional[int]
    meld_tiles = None  # type: Optional[List[int]]

    @property
    def is_agari(self) -> bool:
        return self.type == 'tsumo' or self.type == 'ron' or self.type == 'chan_kan'


        self.type = 'discard'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class RiichiEvent(object):
    def __init__(self, player_seat: int, discard_tile: int):
        self.player_seat = player_seat
        self.type = 'riichi'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class PonEvent(object):
    def __init__(self, player_seat: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_seat = player_seat
        self.type = 'pon'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class ChiEvent(object):
    def __init__(self, player_seat: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_seat = player_seat
        self.type = 'chi'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class AnKanEvent(object):
    def __init__(self, player_seat: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_seat = player_seat
        self.type = 'ankan'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class MinKanEvent(object):
    def __init__(self, player_seat: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_seat = player_seat
        self.type = 'minkan'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class KaKanEvent(object):
    def __init__(self, player_seat: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_seat = player_seat
        self.type = 'kakan'
        self.discard_tile = discard_tile
        self.meld_tiles = (meld_tile1, meld_tile2)


class AgariEvent(object):
    def __init__(self, player_seat: int):
        self.player_seat = player_seat
        self.type = 'agari'
        self.discard_tile = None
        self.meld_tiles = None


class ChankanEvent(object):
    def __init__(self, player_seat: int, discard_tile: int):
        self.player_seat = player_seat
        self.type = 'chankan'
        self.discard_tile = None
        self.meld_tiles = None


class NoneEvent(object):
    def __init__(self, player_seat: int):
        self.player_seat = player_seat
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

EndEvent = Union[
    AgariEvent,
    ChankanEvent
]

Event = Union[
    DiscardEvent,
    RiichiEvent,
    MeldEvent,
    EndEvent,
    NoneEvent
]
