# -*- coding: utf-8 -*-
from typing import List, Optional

from .event import Event

from mahjong.table import Table
from mahjong.player import PlayerInterface


class PlayerObservation(object):
    def __init__(self, player: PlayerInterface, tiles: Optional[List[int]]):
        self.seat = player.seat
        self.scores = player.scores
        self.tiles = tiles


class Observation(object):
    def __init__(self, table: Table, events: List[Event]):
        self.player = PlayerObservation(table.player)
        self.players = [PlayerObservation(x) for x in table.players]
        self.dealer_seat = table.dealer_seat
        self.count_of_riichi_sticks = table.count_of_riichi_sticks
        self.count_of_honba_sticks = table.count_of_honba_sticks

        self.events = events
