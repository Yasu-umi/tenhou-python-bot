# -*- coding: utf-8 -*-
from game.event import PonEvent, ChiEvent, AnKanEvent, MinKanEvent, KaKanEvent, TsumoEvent, RonEvent, ChanKanEvent
from game.event import DiscardEvent, RiichiEvent, KyushuKyuhaiEvent, NoneEvent

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
            method = ActionExcutor._execute_discard
        elif isinstance(selected_event, RiichiEvent):
            method = ActionExcutor._execute_riichi
        elif isinstance(selected_event, PonEvent):
            method = ActionExcutor._execute_pon
        elif isinstance(selected_event, ChiEvent):
            method = ActionExcutor._execute_chi
        elif isinstance(selected_event, AnKanEvent):
            method = ActionExcutor._execute_an_kan
        elif isinstance(selected_event, MinKanEvent):
            method = ActionExcutor._execute_min_kan
        elif isinstance(selected_event, KaKanEvent):
            method = ActionExcutor._execute_ka_kan
        elif isinstance(selected_event, TsumoEvent):
            method = ActionExcutor._execute_tsumo
        elif isinstance(selected_event, RonEvent):
            method = ActionExcutor._execute_ron
        elif isinstance(selected_event, ChanKanEvent):
            method = ActionExcutor._execute_chan_kan
        elif isinstance(selected_event, KyushuKyuhaiEvent):
            method = ActionExcutor._execute_kyushu_kyuhai
        elif isinstance(selected_event, NoneEvent):
            return False
        else:
            raise 'NotFoundEvent'
        return method(
            table=table, client=client, _observation=_observation, selected_event=selected_event
        )

    @staticmethod
    def _execute_discard(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        ActionExcutor._discard(client=client, _observation=_observation, selected_event=selected_event)
        return False

    @staticmethod
    def _execute_riichi(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        if len([client for client in table.clients if client.in_riichi]) == 3:
            return True
        client.in_riichi = True
        ActionExcutor._discard(client=client, _observation=_observation, selected_event=selected_event)
        table.count_of_honba_sticks += 1
        client.scores += 1000
        return False

    @staticmethod
    def _execute_pon(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return False

    @staticmethod
    def _execute_chi(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return False

    @staticmethod
    def _execute_an_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return False

    @staticmethod
    def _execute_min_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return False

    @staticmethod
    def _execute_ka_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return False

    @staticmethod
    def _execute_tsumo(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return True

    @staticmethod
    def _execute_ron(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return True

    @staticmethod
    def _execute_chan_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return False

    @staticmethod
    def _execute_kyushu_kyuhai(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        return False

    @staticmethod
    def _execute_none(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
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
