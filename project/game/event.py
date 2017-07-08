# -*- coding: utf-8 -*-
from typing import Union


class DiscardEvent(object):
    def __init__(self, player_seat: int, discard_tile: int):
        self.player_seat = player_seat
        self.type = 'discard'
        self.discard_tile = discard_tile
        self.meld_tiles = None


class ReachEvent(object):
    def __init__(self, player_seat: int, discard_tile: int):
        self.player_seat = player_seat
        self.type = 'reach'
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


class KanEvent(object):
    def __init__(self, player_seat: int, discard_tile: int, meld_tile1: int, meld_tile2: int):
        self.player_seat = player_seat
        self.type = 'kan'
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
    KanEvent
]

EndEvent = Union[
    AgariEvent,
    ChankanEvent
]

Event = Union[
    DiscardEvent,
    ReachEvent,
    MeldEvent,
    EndEvent,
    NoneEvent
]
