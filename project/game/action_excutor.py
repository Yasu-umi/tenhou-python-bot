# -*- coding: utf-8 -*-
from typing import List, Optional, Union

from game.event import (PonEvent, ChiEvent, AnKanDeclarationEvent, MinKanDeclarationEvent, KaKanDeclarationEvent,
                        TsumoEvent, RinshanTsumoEvent, RiichiEvent, TsumoAgariEvent, RonAgariEvent, ChanKanAgariEvent, KyushuKyuhaiEvent, NoneEvent)
from game.exceptions import NotFoundNewTileException, NotFoundDiscardTileException, NotFromWhoException, ThisRoundAlreadyEndsException

from mahjong.ai.agari import Agari
from mahjong.tile import TilesConverter
from mahjong.meld import Meld, PON_TYPE, CHI_TYPE, KAN_TYPE

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
        observation: 'Observation',
        selected_event: 'Event',
    ) -> bool:
        if isinstance(selected_event, TsumoEvent):
            return ActionExcutor._execute_tsumo(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RinshanTsumoEvent):
            return ActionExcutor._execute_rinshan_tsumo(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RiichiEvent):
            return ActionExcutor._execute_riichi(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, PonEvent):
            return ActionExcutor._execute_pon(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, ChiEvent):
            return ActionExcutor._execute_chi(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, AnKanDeclarationEvent):
            return ActionExcutor._execute_an_kan_declaration(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, MinKanDeclarationEvent):
            return ActionExcutor._execute_min_kan_declaration(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, KaKanDeclarationEvent):
            return ActionExcutor._execute_ka_kan_declaration(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, TsumoAgariEvent):
            return ActionExcutor._execute_tsumo_agari(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, RonAgariEvent):
            return ActionExcutor._execute_ron_agari(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, ChanKanAgariEvent):
            return ActionExcutor._execute_chan_kan_agari(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, KyushuKyuhaiEvent):
            return ActionExcutor._execute_kyushu_kyuhai(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        elif isinstance(selected_event, NoneEvent):
            return ActionExcutor._execute_none(
                table=table, client=client, observation=observation, selected_event=selected_event
            )
        else:
            raise 'NotFoundEvent'

    @staticmethod
    def _execute_tsumo(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'TsumoEvent',
    ) -> bool:
        ActionExcutor._discard(client=client, observation=observation, selected_event=selected_event)
        return False

    @staticmethod
    def _execute_rinshan_tsumo(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'RinshanTsumoEvent',
    ) -> bool:
        ActionExcutor._discard(client=client, observation=observation, selected_event=selected_event)
        return False

    @staticmethod
    def _execute_riichi(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'RiichiEvent',
    ) -> bool:
        client.in_riichi = True
        ActionExcutor._discard(client=client, observation=observation, selected_event=selected_event)
        table.count_of_honba_sticks += 1
        client.scores -= 1000
        # 四家立直の場合ゲーム終了
        return len([client for client in table.clients if client.in_riichi]) == 4

    @staticmethod
    def _execute_pon(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'PonEvent',
    ) -> bool:
        return ActionExcutor._execute_pon_or_chi(
            table=table, client=client, observation=observation, selected_event=selected_event, type=Meld.PON,
        )

    @staticmethod
    def _execute_chi(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'ChiEvent',
    ) -> bool:
        return ActionExcutor._execute_pon_or_chi(
            table=table, client=client, observation=observation, selected_event=selected_event, type=Meld.CHI,
        )

    @staticmethod
    def _execute_pon_or_chi(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: Union['ChiEvent', 'PonEvent'],
        type: Union['PON_TYPE', 'CHI_TYPE'],
    ) -> bool:
        from_event = next(filter(lambda x: x.discard_tile == selected_event.meld_tiles[0], observation.events), None)
        from_player = from_event.get_player(table=table) if from_event is not None else None
        from_who = next(filter(lambda x: from_player is not None and x.seat == from_player.seat, observation.players), None) if from_player is not None else None
        if from_who is None:
            raise NotFromWhoException
        meld = Meld.init(
            who=observation.player,
            tiles=list(selected_event.meld_tiles),
            type=type,
            from_who=from_who,
            called_tile=selected_event.meld_tiles[0],
        )
        client.tiles = [tile for tile in client.tiles if tile not in selected_event.meld_tiles and tile != selected_event.discard_tile]
        client.melds.append(meld)
        return False

    @staticmethod
    def _execute_an_kan_declaration(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'AnKanDeclarationEvent',
    ) -> bool:
        return ActionExcutor._execute_kan(
            table=table, client=client, observation=observation, selected_event=selected_event, type=Meld.KAN,
        )

    @staticmethod
    def _execute_min_kan_declaration(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'MinKanDeclarationEvent',
    ) -> bool:
        return ActionExcutor._execute_kan(
            table=table, client=client, observation=observation, selected_event=selected_event, type=Meld.KAN,
        )

    @staticmethod
    def _execute_kan(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: Union['AnKanDeclarationEvent','MinKanDeclarationEvent'],
        type: 'KAN_TYPE',
    ) -> bool:
        from_event = next(filter(lambda x: x.discard_tile == selected_event.meld_tiles[0], observation.events), None)
        from_seat = table.clients[from_event.player_id].seat if from_event is not None else None
        # AnKanDeclarationの場合from_whoはNoneになる
        from_who = next(filter(lambda x: x.seat == from_seat, observation.players), None) if from_seat is not None else None
        meld = Meld.init(
            who=observation.player,
            tiles=list(selected_event.meld_tiles),
            type=type,
            from_who=from_who,
            called_tile=selected_event.meld_tiles[0],
            opened=isinstance(selected_event.type, AnKanDeclarationEvent)
        )
        client.tiles = [tile for tile in client.tiles if tile not in selected_event.meld_tiles]
        client.melds.append(meld)
        return False

    @staticmethod
    def _execute_ka_kan_declaration(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'KaKanDeclarationEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_tsumo_agari(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'TsumoAgariEvent',
    ) -> bool:
        return True

    @staticmethod
    def _execute_ron_agari(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'RonAgariEvent',
    ) -> bool:
        last_discard_event: Optional['Event'] = None
        events: List[Union['RonAgariEvent', 'NoneEvent']] = []
        for event in reversed(table.selected_events):
            if isinstance(event, NoneEvent) or isinstance(event, RonAgariEvent):
                events.append(event)
            else:
                last_discard_event = event
                break
        if last_discard_event is None:
            raise NotFoundDiscardTileException
        if len(events) == 3:
            return True
        if len(events) == 2:
            table._clients_by_seat_range(
                start=last_discard_event.get_player(table=table).seat,
                end=events[0].get_player(table=table).seat
            )
            return True
        if len(events) == 1:
            return True
        raise ThisRoundAlreadyEndsException

    @staticmethod
    def _execute_chan_kan_agari(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'ChanKanAgariEvent',
    ) -> bool:
        return True

    @staticmethod
    def _execute_kyushu_kyuhai(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'KyushuKyuhaiEvent',
    ) -> bool:
        return False

    @staticmethod
    def _execute_none(
        table: 'GameTable',
        client: 'GameClient',
        observation: 'Observation',
        selected_event: 'NoneEvent',
    ) -> bool:
        return False

    @staticmethod
    def _discard(client: 'GameClient', observation: 'Observation', selected_event: 'HasDiscardTileEvent') -> None:
        if observation.player.new_tile == selected_event.discard_tile:
            client.tiles = observation.player.tiles
        elif selected_event.discard_tile in observation.player.tiles:
            tiles = observation.player.tiles
            tiles.remove(selected_event.discard_tile)
            if observation.player.new_tile is not None:
                tiles.append(observation.player.new_tile)
            else:
                raise NotFoundNewTileException
            client.tiles = tiles
        else:
            raise NotFoundDiscardTileException

    @staticmethod
    def _is_agari(tiles: List[int], melds: List['Meld']) -> bool:
        _melds = [TilesConverter.to_34_array(meld.tiles) for meld in melds]
        agari = Agari()
        return agari.is_agari(tiles=TilesConverter.to_34_array(tiles), melds=_melds)
