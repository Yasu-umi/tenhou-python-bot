# -*- coding: utf-8 -*-
from typing import List, Optional

from game.event import Event

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.client import GameClient  # noqa
    from game.event import Event  # noqa
    from mahjong.meld import Meld  # noqa


class PlayerObservation(object):
    seat = 0
    scores = 0
    melds: List['Meld'] = []

    def __init__(
        self,
        seat: int,
        scores: int,
        tiles: Optional[List[int]],
        melds: List['Meld'] = [],
        new_tile: Optional[int] = None
    ) -> None:
        self.seat = seat
        self.scores = scores
        self.tiles = tiles
        self.melds = melds
        self.new_tile = new_tile


class OwnPlayer(PlayerObservation):
    tiles: List[int] = []

    def __init__(
        self,
        seat: int,
        scores: int,
        tiles: List[int],
        melds: List['Meld'] = [],
        new_tile: Optional[int] = None
    ) -> None:
        self.seat = seat
        self.scores = scores
        self.tiles = tiles
        self.melds = melds
        self.new_tile = new_tile

    @staticmethod
    def from_game_client(client: 'GameClient', new_tile: Optional[int]) -> 'OwnPlayer':
        return OwnPlayer(
            seat=client.seat,
            scores=client.scores,
            tiles=client.tiles,
            melds=client.melds,
            new_tile=new_tile,
        )


class EnemyPlayer(PlayerObservation):
    tiles: None = None

    def __init__(
        self,
        seat: int,
        scores: int,
        tiles: None = None,
        melds: List['Meld'] = [],
        new_tile: Optional[int] = None
    ) -> None:
        self.seat = seat
        self.scores = scores
        self.tiles = tiles
        self.melds = melds
        self.new_tile = new_tile

    @staticmethod
    def from_game_client(client: 'GameClient') -> 'EnemyPlayer':
        return EnemyPlayer(
            seat=client.seat,
            scores=client.scores,
            melds=client.melds,
        )


class Observation(object):
    def __init__(
        self,
        player: 'OwnPlayer',
        players: List['PlayerObservation'],
        dealer_seat: int,
        count_of_riichi_sticks: int,
        count_of_honba_sticks: int,
        dora_indicators: List[int],
        events: List['Event'],
    ) -> None:
        self.player = player
        self.players = players
        self.dealer_seat = dealer_seat
        self.count_of_riichi_sticks = count_of_riichi_sticks
        self.count_of_honba_sticks = count_of_honba_sticks
        self.dora_indicators = dora_indicators
        self.events = events
