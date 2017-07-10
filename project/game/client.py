# -*- coding: utf-8 -*-
import random
from typing import List

from game.event import Event
from game.observation import Observation, PlayerObservation

from mahjong.constants import EAST, SOUTH, WEST, NORTH


class ClientInterface(object):
    def action(
      self,
      events: List[Event],
      _observation: Observation
    ) -> Event:
        return random.choice(events)


class GameClient(object):
    id = 0
    scores = 0
    seat = 0
    in_riichi = False

    tiles = []  # type: List[int]
    melds = []  # type: List[Meld]

    def __init__(self, id: int, client: ClientInterface):
        self.id = id
        self.client = client

    def action(
      self,
      events: List[Event],
      _observation: Observation
    ) -> Event:
        return self.client.action(events=events, _observation=_observation)

    def to_player_observation(self, new_tile: int) -> PlayerObservation:
        return PlayerObservation(
            seat=self.seat,
            scores=self.scores,
            tiles=self.tiles,
            melds=self.melds,
            new_tile=new_tile,
        )

    @property
    def is_open_hand(self):
        opened_melds = [x for x in self.melds if x.opened]
        return len(opened_melds) > 0

    @staticmethod
    def player_wind(dealer_seat):
        if dealer_seat == 0:
            return EAST
        elif dealer_seat == 1:
            return NORTH
        elif dealer_seat == 2:
            return WEST
        else:
            return SOUTH
