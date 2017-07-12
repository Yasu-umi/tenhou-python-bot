# -*- coding: utf-8 -*-
from typing import List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.event import Event
    from mahjong.meld import Meld


class PlayerObservation(object):
    seat = 0
    scores = 0
    melds = []  # type: List[Meld]

    def __init__(
        self,
        seat: int,
        scores: int,
        tiles: Optional[List[int]],
        melds: List['Meld'] = [],
        new_tile: Optional[int] = None
    ):
        self.seat = seat
        self.scores = scores
        self.tiles = tiles
        self.melds = melds
        self.new_tile = new_tile


class Observation(object):
    def __init__(
        self,
        player: PlayerObservation,
        players: List[PlayerObservation],
        dealer_seat: int,
        count_of_riichi_sticks: int,
        count_of_honba_sticks: int,
        events: List['Event'],
    ):
        self.player = player
        self.players = players
        self.dealer_seat = dealer_seat
        self.count_of_riichi_sticks = count_of_riichi_sticks
        self.count_of_honba_sticks = count_of_honba_sticks

        self.events = events
