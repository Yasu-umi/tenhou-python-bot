# -*- coding: utf-8 -*-
import copy
import random
from typing import List

from mahjong.constants import EAST, SOUTH, WEST, NORTH
from mahjong.ai.shanten import Shanten
from mahjong.tile import TilesConverter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.event import Event  # noqa
    from game.observation import Observation  # noqa
    from mahjong.meld import Meld  # noqa


class ClientInterface(object):
    def action(
      self,
      events: List['Event'],
      _observation: 'Observation'
    ) -> 'Event':
        return random.choice(events)


class BaseClient(ClientInterface):
    def _calculate_shanten(self, _observation: 'Observation', event: 'Event') -> int:
        shanten = Shanten()
        tiles = copy.deepcopy(_observation.player.tiles)
        if _observation.player.new_tile is not None:
            tiles.append(_observation.player.new_tile)
        if event.discard_tile is not None:
            tiles.remove(event.discard_tile)
        tiles_34 = TilesConverter.to_34_array(tiles)
        return shanten.calculate_shanten(tiles_34=tiles_34)

    def action(
      self,
      events: List['Event'],
      _observation: 'Observation'
    ) -> 'Event':
        agari_event = next(filter(lambda x: x.is_agari, events), None)
        if agari_event is not None:
            print(agari_event)
            return agari_event
        else:
            event = min(events, key=(lambda x: self._calculate_shanten(_observation=_observation, event=x)))
            return event


class GameClient(object):
    id = 0
    scores = 0
    seat = 0
    in_riichi = False

    tiles: List[int] = []
    melds: List['Meld'] = []

    def __init__(self, id: int, client: 'ClientInterface') -> None:
        self.id = id
        self.client = client

    def action(
      self,
      events: List['Event'],
      _observation: 'Observation',
    ) -> 'Event':
        return self.client.action(events=events, _observation=_observation)

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
