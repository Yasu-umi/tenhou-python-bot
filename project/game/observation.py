# -*- coding: utf-8 -*-
from typing import List, Optional

from .event import Event

from mahjong.table import Table
from mahjong.player import PlayerInterface


class PlayerObservation(object):
    seat = 0
    scores = 0
    melds = []  # type: List[Meld]

    def __init__(self, player: PlayerInterface, tiles: Optional[List[int]], new_tile: Optional[int]):
        self.seat = player.seat
        self.scores = player.scores
        if player.melds is not None:
            self.melds = player.melds
        self.tiles = tiles
        self.new_tile = new_tile


class Observation(object):
    def __init__(self, table: Table, events: List[Event]):
        self.player = PlayerObservation(table.player)
        self.players = [PlayerObservation(x) for x in table.players]
        self.dealer_seat = table.dealer_seat
        self.count_of_riichi_sticks = table.count_of_riichi_sticks
        self.count_of_honba_sticks = table.count_of_honba_sticks

        self.events = events
