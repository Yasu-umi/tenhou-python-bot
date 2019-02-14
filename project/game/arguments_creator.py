# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional
import itertools

from game.event import (PonEvent, ChiEvent, AnKanDeclarationEvent, MinKanDeclarationEvent, KaKanDeclarationEvent,
                        TsumoEvent, RinshanTsumoEvent, RiichiEvent, TsumoAgariEvent, RonAgariEvent, ChanKanAgariEvent, KyushuKyuhaiEvent, NoneEvent)
from game.exceptions import ThisRoundAlreadyEndsException, NotFoundNextSeatPlayerException, FirstEventIsNoneException, NotFoundLastEventPlayerException, NotFoundlastDiscardEventException, NotFoundNewTileException
from game.observation import Observation, OwnPlayer, EnemyPlayer

from mahjong.ai.agari import Agari
from mahjong.constants import TERMINAL_INDICES
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
        next_players: List['GameClient'] = []

        if isinstance(last_event, TsumoAgariEvent):
            raise ThisRoundAlreadyEndsException

        if isinstance(last_event, RonAgariEvent):
            last_not_ron_event: Optional['Event'] = None
            ron_events: List['RonAgariEvent'] = []
            for event in reversed(table.selected_events):
                if isinstance(event, RonAgariEvent):
                    ron_events.append(event)
                else:
                    last_not_ron_event = event
                    break
            if (last_not_ron_event is None) or (not last_not_ron_event.has_discard_tile):
                raise NotFoundlastDiscardEventException
            if len(ron_events) > 2:
                raise ThisRoundAlreadyEndsException

            last_not_ron_event_player = last_not_ron_event.get_player(table=table)
            last_event_player = last_event.get_player(table=table)
            new_tile = last_not_ron_event.discard_tile
            if new_tile is None:
                raise NotFoundNewTileException

            next_players = table._clients_by_seat_range(
                start=last_event_player.next_player_seat,
                end=last_not_ron_event_player.seat
            )
            return ArgumentsCreator._after_has_discard_event(
                table=table,
                last_event_player_seat=last_not_ron_event_player.seat,
                next_players=next_players,
                new_tile=new_tile,
                only_ron=True,
            )

        if last_event is None:
            next_player_seat = 0
            action_client = next(filter(lambda x: x.seat == next_player_seat, table.clients), None)
            if action_client is None:
                raise NotFoundNextSeatPlayerException
            new_tile = table.yama.pop()

            events = ArgumentsCreator._add_tsumo_events(
                events=events, action_client=action_client, new_tile=new_tile
            )
            events = ArgumentsCreator._add_tsumo_agari_events(
                table=table, events=events, action_client=action_client, new_tile=new_tile
            )
            # TODO: KyushuKyuhaiEventを加える
            return events, action_client, new_tile

        if isinstance(last_event, NoneEvent):
            last_has_discard_event: Optional['Event'] = None
            last_not_none_event: Optional['Event'] = None
            for event in reversed(table.selected_events):
                if event.has_discard_tile:
                    last_has_discard_event = event
                if not isinstance(event, NoneEvent):
                    last_not_none_event = event
                    break

            if last_not_none_event is None or last_has_discard_event is None:
                raise FirstEventIsNoneException
            if last_not_none_event.has_discard_tile or isinstance(last_not_none_event, RonAgariEvent):
                last_event_player = last_event.get_player(table=table)
                last_has_discard_event_player = table.clients[last_has_discard_event.player_id]
                if last_has_discard_event_player is None:
                    raise NotFoundLastEventPlayerException
                new_tile = last_has_discard_event.discard_tile
                if new_tile is None:
                    raise NotFoundNewTileException

                next_players = table._clients_by_seat_range(
                    start=last_event_player.next_player_seat,
                    end=last_has_discard_event_player.seat
                )
                return ArgumentsCreator._after_has_discard_event(
                    table=table,
                    last_event_player_seat=last_event_player.seat,
                    next_players=next_players,
                    new_tile=new_tile,
                    only_ron=isinstance(last_not_none_event, RonAgariEvent),
                )
            if last_not_none_event.is_kan_declaration:
                action_client = table.clients[last_not_none_event.player_id]
                new_tile = table.rinshanhai.pop()
                events = ArgumentsCreator._add_rinshan_tsumo_events(
                    events=events, action_client=action_client, new_tile=new_tile
                )
                return events, action_client, new_tile
            raise Exception('NotImplimented')

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
                table=table, events=events, action_client=action_client, new_tile=new_tile
            )
            return events, action_client, new_tile

        if last_event.has_discard_tile:
            new_tile = last_event.discard_tile
            if new_tile is None:
                raise NotFoundNewTileException

            last_event_player = table.clients[last_event.player_id]
            if last_event_player is None:
                raise NotFoundLastEventPlayerException
            # ポン・カン・アガリの判定を行う順番に並んだplayerの配列
            next_players = []
            for i in range(1, 4):
                next_player_seat = last_event_player.n_next_player_seat(i)
                next_player = next(filter(lambda x: x.seat == next_player_seat, table.clients), None)
                if next_player is None:
                    raise NotFoundNextSeatPlayerException
                next_players.append(next_player)

            return ArgumentsCreator._after_has_discard_event(
                table=table,
                last_event_player_seat=last_event_player.seat,
                next_players=next_players,
                new_tile=new_tile,
            )

        last_event_player = last_event.get_player(table=table)
        next_player_seat = last_event_player.next_player_seat
        action_client = next(filter(lambda x: x is not None and x.seat == next_player_seat, table.clients), None)
        if action_client is None:
            raise NotFoundNextSeatPlayerException
        new_tile = table.yama.pop()

        events = ArgumentsCreator._add_tsumo_and_tsumo_agari_and_riichi_events(
            table=table, events=events, action_client=action_client, new_tile=new_tile
        )
        return events, action_client, new_tile

    @staticmethod
    def _after_has_discard_event(
        table: 'GameTable',
        last_event_player_seat: int,
        next_players: List['GameClient'],
        new_tile: int,
        only_ron: bool = False,
    ) -> Tuple[List['Event'], 'GameClient', Optional[int]]:
        events: List['Event'] = []
        for next_player in next_players:
            action_client = next_player

            events = ArgumentsCreator._add_ron_agari_events(
                table=table, events=events, action_client=action_client, new_tile=new_tile
            )
            if not only_ron:
                kannable_tiles = ArgumentsCreator._get_kannable_tiles(
                    action_client=action_client, discard_tile=new_tile
                )
                if kannable_tiles is not None:
                    meld_part = kannable_tiles
                    events = ArgumentsCreator._add_min_kan_events(
                        events=events, action_client=action_client, new_tile=new_tile, meld_part=meld_part
                    )

                ponnable_tiles = ArgumentsCreator._get_ponnable_tiles(
                    action_client=action_client, discard_tile=new_tile
                )
                if ponnable_tiles is not None:
                    meld_parts = ponnable_tiles
                    events = ArgumentsCreator._add_pon_events(
                        events=events, action_client=action_client, new_tile=new_tile, meld_parts=meld_parts
                    )

            # ポン・カン・アガリのいずれも不可能であった場合、次のプレイヤーを見る
            if len(events) > 0:
                # カン・ポン可能なプレイヤーがチーも可能な場合、チーイベントも一緒に渡す
                chiable_seat = (last_event_player_seat + 1) % 4
                if action_client.seat == chiable_seat:
                    chiable_tiles = ArgumentsCreator._get_chiable_tiles(
                        action_client=action_client, discard_tile=new_tile
                    )
                    if chiable_tiles is not None:
                        meld_parts = chiable_tiles
                        events = ArgumentsCreator._add_chi_events(
                            events=events, action_client=action_client, new_tile=new_tile, meld_parts=meld_parts
                        )
                events = ArgumentsCreator._add_none_events(
                    events=events, action_client=action_client
                )
                return events, action_client, new_tile
            else:
                continue

        if only_ron:
            raise ThisRoundAlreadyEndsException

        # 全てのプレイヤーがポン・カン・アガリのいずれも不可能であった場合、チーが可能か見る
        chiable_seat = last_event_player_seat + 1 if last_event_player_seat < 2 else 0
        _action_client = next(filter(lambda x: x is not None and x.seat == chiable_seat, table.clients), None)
        if _action_client is None:
            raise NotFoundNextSeatPlayerException
        if _action_client in next_players:
            chiable_tiles = ArgumentsCreator._get_chiable_tiles(
                action_client=_action_client, discard_tile=new_tile
            )
            if chiable_tiles is not None:
                meld_parts = chiable_tiles
                events = ArgumentsCreator._add_chi_events(
                    events=events, action_client=_action_client, new_tile=new_tile, meld_parts=meld_parts
                )
                events = ArgumentsCreator._add_none_events(
                    events=events, action_client=_action_client
                )
                return events, _action_client, new_tile

        # 全てのプレイヤーがポン・カン・アガリ・チーのいずれも不可能であった場合、次のツモに移行
        next_player_seat = chiable_seat
        _action_client = next(filter(lambda x: x is not None and x.seat == next_player_seat, table.clients), None)
        if _action_client is None:
            raise NotFoundNextSeatPlayerException
        new_tile = table.yama.pop()

        events = ArgumentsCreator._add_tsumo_and_tsumo_agari_and_riichi_events(
            table=table, events=events, action_client=_action_client, new_tile=new_tile
        )
        return events, _action_client, new_tile

    @staticmethod
    def _add_tsumo_and_tsumo_agari_and_riichi_events(table: 'GameTable', events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        events = ArgumentsCreator._add_tsumo_events(
            events=events, action_client=action_client, new_tile=new_tile
        )
        events = ArgumentsCreator._add_tsumo_agari_events(
            table=table, events=events, action_client=action_client, new_tile=new_tile
        )
        events = ArgumentsCreator._add_riichi_events(
            table=table, events=events, action_client=action_client, new_tile=new_tile
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
    def _add_riichi_events(table: 'GameTable', events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        riichi_events: List['Event'] = [
            RiichiEvent(player_id=action_client.id, discard_tile=discard_tile)
            for discard_tile in action_client.tiles + [new_tile]
            if ArgumentsCreator._can_riichi(
                table=table,
                action_client=action_client,
                tiles=action_client.tiles + [new_tile],
                discard_tile=discard_tile
            )
        ]
        return events + riichi_events

    @staticmethod
    def _add_rinshan_tsumo_events(events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        rinshan_tsumo_events: List['Event'] = [
            RinshanTsumoEvent(player_id=action_client.id, discard_tile=discard_tile)
            for discard_tile in action_client.tiles + [new_tile]
        ]
        return events + rinshan_tsumo_events

    @staticmethod
    def _add_tsumo_agari_events(table: 'GameTable', events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        tsumo_agari_events: List['Event'] = []
        win_event = TsumoAgariEvent(player_id=action_client.id)
        is_agari = ArgumentsCreator._is_agari(table=table, client=action_client, win_event=win_event)
        if is_agari:
            tsumo_agari_events.append(win_event)
        return events + tsumo_agari_events

    @staticmethod
    def _add_ron_agari_events(table: 'GameTable', events: List['Event'], action_client: 'GameClient', new_tile: int) -> List['Event']:
        ron_agari_events: List['Event'] = []
        win_event = RonAgariEvent(player_id=action_client.id)
        is_agari = ArgumentsCreator._is_agari(table=table, client=action_client, win_event=win_event)
        if is_agari:
            ron_agari_events.append(win_event)
        return events + ron_agari_events

    @staticmethod
    def _add_min_kan_events(
        events: List['Event'],
        action_client: 'GameClient',
        new_tile: int,
        meld_part: Tuple[int, int, int],
    ) -> List['Event']:
        min_kan_events: List['Event'] = []
        for tile in action_client.tiles:
            # 喰い替え防止の条件
            if (tile // 4) != (new_tile // 4):
                discard_tile = tile
                min_kan_events.append(
                    MinKanDeclarationEvent(
                        player_id=action_client.id,
                        meld_tiles=(new_tile, meld_part[0], meld_part[1], meld_part[2]),
                    )
                )
        return events + min_kan_events

    @staticmethod
    def _add_pon_events(
        events: List['Event'],
        action_client: 'GameClient',
        new_tile: int,
        meld_parts: List[Tuple[int, int]],
    ) -> List['Event']:
        pon_events: List['Event'] = []
        for tile in action_client.tiles:
            discard_tile = tile
            for meld_part in meld_parts:
                # 喰い替え防止の条件
                if (tile // 4) != (new_tile // 4):
                    pon_events.append(
                        PonEvent(
                            player_id=action_client.id,
                            discard_tile=discard_tile,
                            meld_tiles=(new_tile, meld_part[0], meld_part[1]),
                        )
                    )
        return events + pon_events

    @staticmethod
    def _add_chi_events(
        events: List['Event'],
        action_client: 'GameClient',
        new_tile: int,
        meld_parts: List[Tuple[int, int]],
    ) -> List['Event']:
        chi_events: List['Event'] = []
        for tile in action_client.tiles:
            discard_tile = tile
            for meld_part in meld_parts:
                # 喰い替え防止の条件作成
                cant_discard_tiles_34 = sorted([new_tile //4, meld_part[0] // 4, meld_part[1] // 4])
                # 前後の牌は同じ種類の数牌の場合、喰い替えに該当
                if ((cant_discard_tiles_34[0] - 1) // 9) == (cant_discard_tiles_34[0] // 9):
                    cant_discard_tiles_34.append(cant_discard_tiles_34[0] - 1)
                if ((cant_discard_tiles_34[2] + 1) // 9) == (cant_discard_tiles_34[2] // 9):
                    cant_discard_tiles_34.append(cant_discard_tiles_34[2] + 1)
                if (tile // 4) not in cant_discard_tiles_34:
                    chi_events.append(
                        ChiEvent(
                            player_id=action_client.id,
                            discard_tile=discard_tile,
                            meld_tiles=(new_tile, meld_part[0], meld_part[1]),
                        )
                    )
        return events + chi_events

    @staticmethod
    def _add_none_events(events: List['Event'], action_client: 'GameClient') -> List['Event']:
        return events + [NoneEvent(player_id=action_client.id)]

    @staticmethod
    def _get_kannable_tiles(action_client: 'GameClient', discard_tile: int) -> Optional[Tuple[int, int, int]]:
        tiles = [tile for tile in action_client.tiles if (tile // 4) == (discard_tile // 4)]
        if len(tiles) == 3:
            return (tiles[0], tiles[1], tiles[2])
        return None

    @staticmethod
    def _get_ponnable_tiles(action_client: 'GameClient', discard_tile: int) -> Optional[List[Tuple[int, int]]]:
        tiles = [tile for tile in action_client.tiles if (tile // 4) == (discard_tile // 4)]
        if len(tiles) == 2:
            return [(tiles[0], tiles[1])]
        if len(tiles) == 3:
            return [(tiles[0], tiles[1]), (tiles[0], tiles[2]), (tiles[1], tiles[2])]
        return None

    @staticmethod
    def _get_chiable_tiles(action_client: 'GameClient', discard_tile: int) -> Optional[List[Tuple[int, int]]]:
        meld_parts = None
        if discard_tile >= 108:
            return meld_parts
        discard_tile_34 = discard_tile // 4
        # 3パターンあるが、同じ種類の数牌のみ
        meld_parts_34 = filter(
            lambda x: (x[0] // 9) == (discard_tile_34 // 9) and (x[1] // 9) == (discard_tile_34 // 9),
            [
                (discard_tile_34 - 2, discard_tile_34 - 1),
                (discard_tile_34 - 1, discard_tile_34 + 1),
                (discard_tile_34 + 1, discard_tile_34 + 2),
            ]
        )
        for meld_part_34 in meld_parts_34:
            tile_1s = list(filter(lambda x: x // 4 == meld_part_34[0], action_client.tiles))
            tile_2s = list(filter(lambda x: x // 4 == meld_part_34[1], action_client.tiles))
            if len(tile_1s) > 0 and len(tile_2s) > 0:
                for tile_1, tile_2 in itertools.product(tile_1s, tile_2s):
                    if meld_parts is None:
                        meld_parts = []
                    meld_parts.append((tile_1, tile_2))
            pass
        return meld_parts

    @staticmethod
    def _is_agari(table: 'GameTable', client: 'GameClient', win_event: 'Event') -> bool:
        (_, _, hand_value) = table._estimate_hand_value(client=client, win_event=win_event)
        return hand_value is not None and hand_value.is_agari

    @staticmethod
    def _can_riichi(table: 'GameTable', action_client: 'GameClient', tiles: List[int], discard_tile: int) -> bool:
        agari = Agari()
        # 次順がない場合リーチできない
        if len(table.yama) < 5:
            return False
        # アンカン以外の鳴きがある場合リーチできない
        if len(action_client.melds) > 0:
            return False
        discard_tiles = [event.discard_tile  // 9 for event in table.selected_events if isinstance(event.discard_tile, int) and event.player_id == action_client.id]
        for new_tile in range(0, 34):
            new_tile_34 = new_tile // 9
            # 捨牌と同じ牌では上がれない
            if new_tile_34 == discard_tile // 9:
                continue
            # 今までに切った牌と同じ牌では上がれない
            if new_tile_34 in discard_tiles:
                continue
            if agari.is_agari(tiles=TilesConverter.to_34_array(tiles) + [new_tile], melds=None):
                return True
        return False
