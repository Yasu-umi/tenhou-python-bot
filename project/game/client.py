# -*- coding: utf-8 -*-
import random
from typing import List

from game.event import Event
from game.observation import Observation

from mahjong.constants import EAST, SOUTH, WEST, NORTH


class ClientInterface(object):
    def action(
      self,
      events: List[Event],
      observation: Observation
    ) -> Event:
        return random.choice(events)


class GameClient(object):
    scores = 0
    seat = 0
    in_riichi = False

    tiles = []  # type: List[int]

    def __init__(self, client: ClientInterface):
        self.client = client

    def action(
      self,
      events: List[Event],
      observation: Observation
    ) -> Event:
        return self.client.action(events, observation)
