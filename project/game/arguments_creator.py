# -*- coding: utf-8 -*-
from typing import List

from game.event import PonEvent, ChiEvent, AnKanEvent, MinKanEvent, KaKanEvent, TsumoEvent, RonEvent, ChanKanEvent, DiscardEvent, RiichiEvent, KyushuKyuhaiEvent, NoneEvent
from game.observation import Observation

from mahjong.ai.agari import Agari
from mahjong.tile import TilesConverter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.client import GameClient
    from game.event import Event
    from game.table import GameTable
    from mahjong.meld import Meld


class ArgumentsCreator:
    @staticmethod
    def create(table: 'GameTable') -> ('Observation', List['Event'], 'GameClient'):
        last_event = table.selected_events[-1] if len(table.selected_events) > 0 else None
        events = []
        if last_event is None:
            action_client = table.client0
            new_tile = table.yama.pop()
            discard_events = [
                DiscardEvent(player_id=action_client.id, discard_tile=discard_tile)
                for discard_tile in action_client.tiles + [new_tile]
            ]
            events.extend(discard_events)

            is_agari = ArgumentsCreator._is_agari(tiles=action_client.tiles + [new_tile], melds=action_client.melds)
            if is_agari:
                events.append(TsumoEvent(player_id=action_client.id))
        elif isinstance(last_event, RonEvent) or isinstance(last_event, TsumoEvent):
            raise 'ThisRoundAlreadyEnds'
        elif isinstance(last_event, DiscardEvent):
            next_player_id = 0 if 2 < last_event.player_id else last_event.player_id + 1
            action_client = table.clients[next_player_id]
            new_tile = last_event.discard_tile
            is_agari = ArgumentsCreator._is_agari(tiles=action_client.tiles + [new_tile], melds=action_client.melds)
            if is_agari:
                events.append(TsumoEvent(player_id=action_client.id))
            else:
                new_tile = table.yama.pop()
                events = ArgumentsCreator._add_discard_events(
                    events=events, action_client=action_client, new_tile=new_tile
                )
        else:
            next_player_id = 0 if 2 < last_event.player_id else last_event.player_id + 1
            action_client = table.clients[next_player_id]
            events = ArgumentsCreator._add_discard_events(events=events, action_client=action_client, new_tile=new_tile)
            events = ArgumentsCreator._add_agari_events(events=events, action_client=action_client, new_tile=new_tile)
        player = action_client.to_player_observation(new_tile)
        clients = table.clients
        clients.remove(action_client)
        players = [client.to_player_observation(None) for client in clients] + [player]
        _observation = Observation(
            player=player,
            players=players,
            dealer_seat=table.dealer_seat,
            count_of_riichi_sticks=table.count_of_riichi_sticks,
            count_of_honba_sticks=table.count_of_honba_sticks,
            events=table.selected_events
        )
        return _observation, events, action_client

    @staticmethod
    def _add_discard_events(events: List['Event'], action_client: 'GameClient', new_tile=int) -> List['Event']:
        discard_events = [
            DiscardEvent(player_id=action_client.id, discard_tile=discard_tile)
            for discard_tile in action_client.tiles + [new_tile]
        ]
        return events + discard_events

    @staticmethod
    def _add_agari_events(events: List['Event'], action_client: 'GameClient', new_tile=int) -> List['Event']:
        agari_events = []
        is_agari = ArgumentsCreator._is_agari(tiles=action_client.tiles + [new_tile], melds=action_client.melds)
        if is_agari:
            agari_events.append(TsumoEvent(player_id=action_client.id))
        return events + agari_events

    @staticmethod
    def _is_agari(tiles: List[int], melds: List['Meld']) -> bool:
        _melds = [TilesConverter.to_34_array(meld.tiles) for meld in melds]
        agari = Agari()
        return agari.is_agari(tiles=TilesConverter.to_34_array(tiles), melds=_melds)