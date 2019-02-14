# -*- coding: utf-8 -*-
import copy
import datetime
from typing import List

from game.client import ClientInterface
# from game.event import NoneEvent, RiichiEvent
from game.event import RiichiEvent
from game.table import GameTable
from mahjong.tile import TilesConverter
from mahjong.ai.shanten import Shanten

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.event import Event  # noqa
    from game.observation import Observation  # noqa


class BaseClient(ClientInterface):
    def _calculate_shanten(self, observation: 'Observation', event: 'Event') -> int:
        shanten = Shanten()
        tiles = copy.deepcopy(observation.player.tiles)
        if observation.player.new_tile is not None:
            tiles.append(observation.player.new_tile)
        if event.discard_tile is not None:
            tiles.remove(event.discard_tile)
        tiles_34 = TilesConverter.to_34_array(tiles)
        open_sets_34 = list(map(lambda x: TilesConverter.to_34_array(x.tiles), observation.player.melds))
        if event.is_meld:
            open_sets_34.append(TilesConverter.to_34_array(event.meld_tiles))
        return shanten.calculate_shanten(tiles_34=tiles_34, open_sets_34=open_sets_34)

    def action(
      self,
      events: List['Event'],
      observation: 'Observation'
    ) -> 'Event':
        agari_event = next(filter(lambda x: x.is_agari, events), None)
        riichi_event = next(filter(lambda x: isinstance(x, RiichiEvent), events), None)
        # none_event = next(filter(lambda x: isinstance(x, NoneEvent), events), None)
        if agari_event is not None:
            print('agari_event', agari_event)
            return agari_event
        if riichi_event is not None:
            print('riichi_event', riichi_event)
            return riichi_event
        # if none_event is not None:
        #     return none_event
        else:
            event = min(events, key=(lambda x: self._calculate_shanten(observation=observation, event=x)))
            return event


if __name__ == '__main__':
    agari_occred = False
    start = datetime.datetime.now().timestamp()
    i = 1

    while True:
        t = GameTable(
            client0=BaseClient(),
            client1=BaseClient(),
            client2=BaseClient(),
            client3=BaseClient(),
        )
        res = True
        while res:
            res = t.next_action()
        for client in t.clients:
            print("id: {}, scores: {}, tiles: {}, melds: {}".format(
                client.id,
                client.scores,
                TilesConverter.to_one_line_string(client.tiles),
                list(map(lambda meld: TilesConverter.to_one_line_string(meld.tiles), client.melds))
            ))
            print("yama: {}".format(t.yama))
        t.next_round()
        for client in t.clients:
            if client.scores != 25000:
                agari_occred = True
        i += 1
        if i % 100 == 0:
            dif = datetime.datetime.now().timestamp() - start
            print("{} end round {}sec".format(i, dif))

        if agari_occred:
            dif = datetime.datetime.now().timestamp() - start
            print("{} end round {}sec".format(i, dif))
            for event in t.selected_events:
                print(event)
            for client in t.clients:
                print("id: {}, scores: {}".format(client.id, client.scores))
            agari_occred = False
