# -*- coding: utf-8 -*-
from typing import Optional

from game.event import (PonEvent, ChiEvent, AnKanDeclarationEvent, MinKanDeclarationEvent, KaKanDeclarationEvent,
                        TsumoEvent, RinshanTsumoEvent, RiichiEvent, TsumoAgariEvent, RonAgariEvent, ChanKanAgariEvent, KyushuKyuhaiEvent, NoneEvent)
from game.exceptions import NotFoundNewTileException, NotFoundDiscardTileException

from mahjong.meld import Meld

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
        if isinstance(selected_event, TsumoEvent):
            return ActionExcutor._execute_tsumo(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RinshanTsumoEvent):
            return ActionExcutor._execute_rinshan_tsumo(
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
        elif isinstance(selected_event, AnKanDeclarationEvent):
            return ActionExcutor._execute_an_kan_declaration(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, MinKanDeclarationEvent):
            return ActionExcutor._execute_min_kan_declaration(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, KaKanDeclarationEvent):
            return ActionExcutor._execute_ka_kan_declaration(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, TsumoAgariEvent):
            return ActionExcutor._execute_tsumo_agari(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RonAgariEvent):
            return ActionExcutor._execute_ron_agari(
                table=table, client=client, _observation=_observation, selected_event=selected_event
            )
        elif isinstance(selected_event, ChanKanAgariEvent):
            return ActionExcutor._execute_chan_kan_agari(
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
    def _execute_tsumo(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'TsumoEvent',
    ) -> bool:
        ActionExcutor._discard(client=client, _observation=_observation, selected_event=selected_event)
        return False

    @staticmethod
    def _execute_rinshan_tsumo(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'RinshanTsumoEvent',
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
        meld = Meld(
            who=None,
            tiles=list(selected_event.meld_tiles),
            type=Meld.PON,
            from_who=None,
            called_tile=selected_event.meld_tiles[0],
            opened=selected_event.opened,
        )
        client.tiles = [tile for tile in client.tiles if tile in selected_event.meld_tiles]
        client.melds.append(meld)
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
    def _execute_an_kan_declaration(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'AnKanDeclarationEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_min_kan_declaration(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'MinKanDeclarationEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_ka_kan_declaration(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'KaKanDeclarationEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_tsumo_agari(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'TsumoAgariEvent',
    ) -> bool:
        return True

    @staticmethod
    def _execute_ron_agari(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'RonAgariEvent',
    ) -> bool:
        return True

    @staticmethod
    def _execute_chan_kan_agari(
        table: 'GameTable',
        client: 'GameClient',
        _observation: 'Observation',
        selected_event: 'ChanKanAgariEvent',
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
                raise NotFoundNewTileException
            client.tiles = tiles
        else:
            raise NotFoundDiscardTileException
