# -*- coding: utf-8 -*-
import random
from typing import List

from mahjong.constants import EAST, SOUTH, WEST, NORTH

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.event import Event  # noqa
    from game.observation import Observation  # noqa
    from mahjong.meld import Meld  # noqa


class ClientInterface(object):
    def action(
      self,
      events: List['Event'],
      observation: 'Observation'
    ) -> 'Event':
        return random.choice(events)


class GameClient(object):
    id = 0
    seat = 0
    scores = 0
    in_riichi = False

    tiles: List[int] = []
    melds: List['Meld'] = []

    @property
    def is_open_hand(self) -> bool:
        opened_melds = [x for x in self.melds if x.opened]
        return len(opened_melds) > 0

    @staticmethod
    def player_wind(dealer_seat: int) -> int:
        if dealer_seat == 0:
            return EAST
        elif dealer_seat == 1:
            return NORTH
        elif dealer_seat == 2:
            return WEST
        else:
            return SOUTH

    @property
    def next_player_seat(self) -> int:
        return self.n_next_player_seat()

    def __init__(self, id: int, client: 'ClientInterface') -> None:
        self.id = id
        self.client = client

    def action(
      self,
      events: List['Event'],
      observation: 'Observation',
    ) -> 'Event':
        return self.client.action(events=events, observation=observation)

    def n_next_player_seat(self, n: int = 1) -> int:
        return (self.seat + n) % 4

    def __str__(self) -> str:
        return "player_id: {}, seat: {}, scores: {}, in_riichi: {}, tiles: {}, melds: {}".format(
            self.id, self.seat, self.scores, self.in_riichi, self.tiles, self.melds
        )

    def __repr__(self) -> str:
        return self.__str__()
