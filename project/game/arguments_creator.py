# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional

from game.event import (PonEvent, ChiEvent, AnKanDeclarationEvent, MinKanDeclarationEvent, KaKanDeclarationEvent,
                        TsumoEvent, RinshanTsumoEvent, RiichiEvent, TsumoAgariEvent, RonAgariEvent, ChanKanAgariEvent, KyushuKyuhaiEvent, NoneEvent)
from game.exceptions import ThisRoundAlreadyEndsException
from game.observation import Observation, OwnPlayer, EnemyPlayer

from mahjong.ai.agari import Agari
from mahjong.tile import TilesConverter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.client import GameClient  # noqa
    from game.event import Event  # noqa
    from game.observation import PlayerObservation  # noqa
    from game.table import GameTable  # noqa
    from mahjong.meld import Meld  # noqa


class ArgumentsCreator:
    @staticmethod
    def create(table: 'GameTable') -> Tuple['Observation', List['Event'], 'GameClient']:
        events, action_client, new_tile = ArgumentsCreator._create_events(table=table)

        player = OwnPlayer.from_game_client(action_client, new_tile)
        clients = table.clients
        clients.remove(action_client)
        players: List['PlayerObservation'] = [EnemyPlayer.from_game_client(client) for client in clients]
        players = players + [player]
        _observation = Observation(
            player=player,
            players=players,
            dealer_seat=table.dealer_seat,
            count_of_riichi_sticks=table.count_of_riichi_sticks,
            count_of_honba_sticks=table.count_of_honba_sticks,
            dora_indicators=table.open_dora_indicators,
            events=table.selected_events
        )
        return _observation, events, action_client

    @staticmethod
    def _create_events(table: 'GameTable') -> Tuple[List['Event'], 'GameClient', Optional[int]]:
        last_event: Optional['Event'] = table.selected_events[-1] if len(table.selected_events) > 0 else None
        events: List['Event'] = []
        new_tile: Optional[int] = None

        if isinstance(last_event, RonAgariEvent) or isinstance(last_event, TsumoAgariEvent):
            raise ThisRoundAlreadyEndsException

        if last_event is None:
            action_client = table.client0
            new_tile = table.yama.pop()

            events = ArgumentsCreator._add_tsumo_events(
                events=events, action_client=action_client, new_tile=new_tile
            )
            events = ArgumentsCreator._add_tsumo_agari_events(
                events=events, action_client=action_client, new_tile=new_tile
            )
            return events, action_client, new_tile

        if isinstance(last_event, AnKanDeclarationEvent) or isinstance(last_event, MinKanDeclarationEvent):
            next_player_id = last_event.player_id
            action_client = table.clients[next_player_id]
            new_tile = table.rinshanhai.pop()

            # FIXME: アンカンの場合ドラを開けるのはリンシャンツモから牌を捨てた後
            table.n_open_dora += 1

            events = ArgumentsCreator._add_rinshan_tsumo_events(
                events=events, action_client=action_client, new_tile=new_tile
            )
            events = ArgumentsCreator._add_tsumo_agari_events(
                events=events, action_client=action_client, new_tile=new_tile
            )
            return events, action_client, new_tile

        if isinstance(last_event, TsumoEvent) or isinstance(last_event, PonEvent) or isinstance(last_event, ChiEvent):
            next_player_id = 0 if 2 < last_event.player_id else last_event.player_id + 1
            action_client = table.clients[next_player_id]
            new_tile = last_event.discard_tile

            other_clients = [client for client in table.clients if action_client.id != client.id]

            events = ArgumentsCreator._add_ron_agari_events(
                events=events, action_client=action_client, new_tile=new_tile
            )

            kannable_client_tiles = ArgumentsCreator._get_kannable_client_tiles(
                clients=other_clients, discard_tile=new_tile
            )
            if kannable_client_tiles is not None:
                action_client = kannable_client_tiles[0]
                meld_part = kannable_client_tiles[1]
                events = ArgumentsCreator._add_min_kan_or_pon_events(
                    events=events, action_client=action_client, new_tile=new_tile, meld_part=meld_part
                )
                events = ArgumentsCreator._add_none_events(
                    events=events, action_client=action_client
                )
                return events, action_client, new_tile

            ponnable_client_tiles = ArgumentsCreator._get_ponnable_client_tiles(
                clients=other_clients, discard_tile=new_tile
            )
            if ponnable_client_tiles is not None:
                action_client = ponnable_client_tiles[0]
                meld_parts = ponnable_client_tiles[1]
                events = ArgumentsCreator._add_pon_events(
                    events=events, action_client=action_client, new_tile=new_tile, meld_parts=meld_parts
                )
                events = ArgumentsCreator._add_none_events(
                    events=events, action_client=action_client
                )
                return events, action_client, new_tile

            new_tile = table.yama.pop()

            events = ArgumentsCreator._add_tsumo_and_tsumo_agari_events(
                events=events, action_client=action_client, new_tile=new_tile
            )
            return events, action_client, new_tile

        next_player_id = 0 if 2 < last_event.player_id else last_event.player_id + 1
        action_client = table.clients[next_player_id]
        new_tile = table.yama.pop()

        events = ArgumentsCreator._add_tsumo_and_tsumo_agari_events(
            events=events, action_client=action_client, new_tile=new_tile
        )
        return events, action_client, new_tile

    @staticmethod
    def _add_tsumo_and_tsumo_agari_events(events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        events = ArgumentsCreator._add_tsumo_events(
            events=events, action_client=action_client, new_tile=new_tile
        )
        events = ArgumentsCreator._add_tsumo_agari_events(
            events=events, action_client=action_client, new_tile=new_tile
        )
        return events

    @staticmethod
    def _add_tsumo_events(events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        tsumo_events: List['Event'] = [
            TsumoEvent(player_id=action_client.id, discard_tile=discard_tile)
            for discard_tile in action_client.tiles + [new_tile]
        ]
        return events + tsumo_events

    @staticmethod
    def _add_rinshan_tsumo_events(events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        rinshan_tsumo_events: List['Event'] = [
            RinshanTsumoEvent(player_id=action_client.id, discard_tile=discard_tile)
            for discard_tile in action_client.tiles + [new_tile]
        ]
        return events + rinshan_tsumo_events

    @staticmethod
    def _add_tsumo_agari_events(events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        tsumo_agari_events: List['Event'] = []
        is_agari = ArgumentsCreator._is_agari(
            tiles=action_client.tiles + [new_tile], melds=action_client.melds
        )
        if is_agari:
            tsumo_agari_events.append(TsumoAgariEvent(player_id=action_client.id))
        return events + tsumo_agari_events

    @staticmethod
    def _add_ron_agari_events(events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        ron_agari_events: List['Event'] = []
        is_agari = ArgumentsCreator._is_agari(
            tiles=action_client.tiles + [new_tile], melds=action_client.melds
        )
        if is_agari:
            ron_agari_events.append(RonAgariEvent(player_id=action_client.id))
        return events + ron_agari_events

    @staticmethod
    def _add_min_kan_or_pon_events(events: List['Event'], action_client: 'GameClient', new_tile: int, meld_part: Tuple[int, int, int]) -> List['Event']:
        min_kan_or_pon_events: List['Event'] = []
        for tile in action_client.tiles:
            # 喰い替え防止の条件
            if (tile // 4) != (new_tile // 4):
                discard_tile = tile
                min_kan_or_pon_events.append(
                    MinKanDeclarationEvent(
                        player_id=action_client.id,
                        discard_tile=discard_tile,
                        meld_tiles=(discard_tile, meld_part[0], meld_part[1], meld_part[2]),
                    )
                )
                for pon_meld_part in [(meld_part[0], meld_part[1]), (meld_part[0], meld_part[2]), (meld_part[1], meld_part[2])]:
                    min_kan_or_pon_events.append(
                        PonEvent(
                            player_id=action_client.id,
                            discard_tile=discard_tile,
                            meld_tiles=(discard_tile, pon_meld_part[0], pon_meld_part[1]),
                        )
                    )
        return events + min_kan_or_pon_events

    @staticmethod
    def _add_pon_events(events: List['Event'], action_client: 'GameClient', new_tile: int, meld_parts: List[Tuple[int, int]]) -> List['Event']:
        pon_events: List['Event'] = []
        for tile in action_client.tiles:
            # 喰い替え防止の条件
            if (tile // 4) != (new_tile // 4):
                discard_tile = tile
                pon_events.extend([
                    PonEvent(
                        player_id=action_client.id,
                        discard_tile=discard_tile,
                        meld_tiles=(discard_tile, meld_part[0], meld_part[1]),
                    )
                    for meld_part in meld_parts
                ])
        return events + pon_events

    @staticmethod
    def _add_none_events(events: List['Event'], action_client: 'GameClient') -> List['Event']:
        return events + [NoneEvent(player_id=action_client.id)]

    @staticmethod
    def _get_kannable_client_tiles(clients: List['GameClient'], discard_tile: int) -> Optional[Tuple['GameClient', Tuple[int, int, int]]]:
        for client in clients:
            tiles = [tile for tile in client.tiles if (tile // 4) == (discard_tile // 4)]
            if len(tiles) == 3:
                return client, (tiles[0], tiles[1], tiles[2])
        return None

    @staticmethod
    def _get_ponnable_client_tiles(clients: List['GameClient'], discard_tile: int) -> Optional[Tuple['GameClient', List[Tuple[int, int]]]]:
        for client in clients:
            tiles = [tile for tile in client.tiles if (tile // 4) == (discard_tile // 4)]
            if len(tiles) == 2:
                return client, [(tiles[0], tiles[1])]
        return None

    @staticmethod
    def _is_agari(tiles: List[int], melds: List['Meld']) -> bool:
        _melds = [TilesConverter.to_34_array(meld.tiles) for meld in melds]
        agari = Agari()
        return agari.is_agari(tiles=TilesConverter.to_34_array(tiles), melds=_melds)
