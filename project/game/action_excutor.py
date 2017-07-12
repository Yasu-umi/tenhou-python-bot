# -*- coding: utf-8 -*-
from game.event import PonEvent, ChiEvent, AnKanEvent, MinKanEvent, KaKanEvent, TsumoEvent, RonEvent, ChanKanEvent, DiscardEvent, RiichiEvent, KyushuKyuhaiEvent, NoneEvent

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.client import GameClient
    from game.event import Event
    from game.observation import Observation
    from game.table import GameTable


class ActionExcutor:
    @staticmethod
    def execute_action(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        if isinstance(selected_event, DiscardEvent):
            return ActionExcutor._execute_discard(
                client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RiichiEvent):
            return ActionExcutor._execute_riichi(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, PonEvent):
            return ActionExcutor._execute_pon(client=client, selected_event=selected_event)
        elif isinstance(selected_event, ChiEvent):
            return ActionExcutor._execute_chi(client=client, selected_event=selected_event)
        elif isinstance(selected_event, AnKanEvent):
            return ActionExcutor._execute_an_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, MinKanEvent):
            return ActionExcutor._execute_min_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, KaKanEvent):
            return ActionExcutor._execute_ka_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, TsumoEvent):
            return ActionExcutor._execute_tsumo()
        elif isinstance(selected_event, RonEvent):
            return ActionExcutor._execute_ron()
        elif isinstance(selected_event, ChanKanEvent):
            return ActionExcutor._execute_chan_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, KyushuKyuhaiEvent):
            return ActionExcutor._execute_kyushu_kyuhai(client=client, selected_event=selected_event)
        elif isinstance(selected_event, NoneEvent):
            return False
        else:
            raise 'NotFoundEvent'

    @staticmethod
    def _execute_discard(client: 'GameClient', _observation: 'Observation', selected_event: 'Event') -> bool:
        ActionExcutor._discard(client=client, _observation=_observation, selected_event=selected_event)
        return False

    @staticmethod
    def _execute_riichi(table: 'GameTable', client: 'GameClient', _observation: 'Observation', selected_event: 'Event') -> bool:
        if len([client for client in table.clients if client.in_riichi]) == 3:
            return True
        client.in_riichi = True
        ActionExcutor._discard(client=client, _observation=_observation, selected_event=selected_event)
        table.count_of_honba_sticks += 1
        client.scores += 1000
        return False

    @staticmethod
    def _execute_pon(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _execute_chi(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _execute_an_kan(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _execute_min_kan(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _execute_ka_kan(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _execute_tsumo() -> bool:
        return True

    @staticmethod
    def _execute_ron() -> bool:
        return True

    @staticmethod
    def _execute_chan_kan(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _execute_kyushu_kyuhai(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _execute_none(client: 'GameClient', selected_event: 'Event') -> bool:
        return False

    @staticmethod
    def _discard(client: 'GameClient', _observation: 'Observation', selected_event: 'Event'):
        if _observation.player.new_tile == selected_event.discard_tile:
            client.tiles = _observation.player.tiles
        elif selected_event.discard_tile in _observation.player.tiles:
            tiles = _observation.player.tiles
            tiles.remove(selected_event.discard_tile)
            tiles.append(_observation.player.new_tile)
            client.tiles = tiles
        else:
            raise 'NotFoundDiscardTile'
