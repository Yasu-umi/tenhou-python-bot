# -*- coding: utf-8 -*-
from game.event import (PonEvent, ChiEvent, AnKanEvent, MinKanEvent, KaKanEvent,
                        DiscardEvent, RiichiEvent, TsumoEvent, RonEvent, ChanKanEvent, KyushuKyuhaiEvent, NoneEvent)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.client import GameClient  # noqa
    from game.event import HasDiscardTileEvent, Event  # noqa
    from game.observation import Observation  # noqa
    from game.table import GameTable  # noqa


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
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RiichiEvent):
            return ActionExcutor._execute_riichi(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, PonEvent):
            return ActionExcutor._execute_pon(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, ChiEvent):
            return ActionExcutor._execute_chi(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, AnKanEvent):
            return ActionExcutor._execute_an_kan(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, MinKanEvent):
            return ActionExcutor._execute_min_kan(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, KaKanEvent):
            return ActionExcutor._execute_ka_kan(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, TsumoEvent):
            return ActionExcutor._execute_tsumo(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RonEvent):
            return ActionExcutor._execute_ron(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, ChanKanEvent):
            return ActionExcutor._execute_chan_kan(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, KyushuKyuhaiEvent):
            return ActionExcutor._execute_kyushu_kyuhai(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, NoneEvent):
            return False
        else:
            raise 'NotFoundEvent'

    @staticmethod
    def _execute_discard(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'DiscardEvent',
    ) -> bool:
        ActionExcutor._discard(client=client, _observation=_observation, selected_event=selected_event)
        return False

    @staticmethod
    def _execute_riichi(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'RiichiEvent',
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
        selected_event: 'PonEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_chi(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'ChiEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_an_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'AnKanEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_min_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'MinKanEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_ka_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'KaKanEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_tsumo(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'TsumoEvent',
    ) -> bool:
        return True

    @staticmethod
    def _execute_ron(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'RonEvent',
    ) -> bool:
        return True

    @staticmethod
    def _execute_chan_kan(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'ChanKanEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_kyushu_kyuhai(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'KyushuKyuhaiEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_none(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'NoneEvent',
    ) -> bool:
        return False

    @staticmethod
    def _discard(client: 'GameClient', _observation: 'Observation', selected_event: 'HasDiscardTileEvent') -> None:
        if _observation.player.new_tile == selected_event.discard_tile:
            client.tiles = _observation.player.tiles
        elif selected_event.discard_tile in _observation.player.tiles:
            tiles = _observation.player.tiles
            tiles.remove(selected_event.discard_tile)
            if _observation.player.new_tile is not None:
                tiles.append(_observation.player.new_tile)
            else:
                raise 'NotFoundNewTile'
            client.tiles = tiles
        else:
            raise 'NotFoundDiscardTile'
