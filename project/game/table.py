# -*- coding: utf-8 -*-
import random
from typing import List

from game.client import ClientInterface, GameClient
from game.event import PonEvent, ChiEvent, AnKanEvent, MinKanEvent, KaKanEvent, TsumoEvent, RonEvent, ChanKanEvent, DiscardEvent, RiichiEvent, MeldEvent, KyushuKyuhaiEvent, NoneEvent, MeldEvent, AgariEvent, Event
from game.observation import Observation

from mahjong.hand import FinishedHand
from mahjong.tile import TilesConverter
from mahjong.meld import Meld
from mahjong.ai.agari import Agari
from mahjong.constants import EAST, SOUTH, WEST, NORTH, AKA_DORA_LIST


class GameTable(object):
    round_number = 0
    count_of_riichi_sticks = 0
    count_of_honba_sticks = 0
    dealer_seat = 0

    selected_events = []  # type: List[Event]

    rinshanhai = []  # type: List[int]
    wanpai = []  # type: List[int]
    yama = []  # type: List[int]

    dora_indexes = [0]  # type: List[int]

    ended_round = False
    ended_game = False

    def __init__(
        self,
        client0=ClientInterface(),
        client1=ClientInterface(),
        client2=ClientInterface(),
        client3=ClientInterface(),
        is_hanchan=True,
        is_open_tanyao=True,
        is_aka=True,
    ):
        self.client0 = GameClient(id=0, client=client0)
        self.client1 = GameClient(id=1, client=client1)
        self.client2 = GameClient(id=2, client=client2)
        self.client3 = GameClient(id=3, client=client3)

        self.is_hanchan = is_hanchan
        self.is_open_tanyao = is_open_tanyao
        self.is_aka = is_aka

        self._init_round()

    def next_action(self) -> bool:
        """
        GameTableの初期化後このメソッドを呼んでください
        Trueが返る間はroundが続いており、next_actionを呼ぶ事でゲームが進みます
        """
        self._update_ended_round()
        if self.ended_round:
            return False

        _observation, events, client = self._create_events_and_observation()

        selected_event = client.action(_observation=_observation, events=events)
        self.selected_events.append(selected_event)

        self.ended_round = self._execute_action(client=client, _observation=_observation, selected_event=selected_event)

        return not self.ended_round

    def _update_ended_round(self):
        last_event = self.selected_events[-1] if len(self.selected_events) > 0 else None
        if len(self.yama) == 0 or (last_event is not None and last_event.is_agari):
            self.ended_round = True

    def _create_events_and_observation(self) -> (Observation, List[Event], GameClient):
        last_event = self.selected_events[-1] if len(self.selected_events) > 0 else None
        events = []
        if last_event is None:
            action_client = self.client0
            new_tile = self.yama.pop()
            discard_events = [
                DiscardEvent(player_id=action_client.id, discard_tile=discard_tile)
                for discard_tile in action_client.tiles + [new_tile]
            ]
            events.extend(discard_events)

            is_agari = self._is_agari(tiles=action_client.tiles + [new_tile], melds=action_client.melds)
            if is_agari:
                events.append(TsumoEvent(player_id=action_client.id))
        elif isinstance(last_event, RonEvent) or isinstance(last_event, TsumoEvent):
            raise 'ThisRoundAlreadyEnds'
        elif isinstance(last_event, DiscardEvent):
            next_player_id = 0 if 2 < last_event.player_id else last_event.player_id + 1
            action_client = self.clients[next_player_id]
            new_tile = last_event.discard_tile
            is_agari = self._is_agari(tiles=action_client.tiles + [new_tile], melds=action_client.melds)
            if is_agari:
                events.append(TsumoEvent(player_id=action_client.id))
            else:
                new_tile = self.yama.pop()
                events = self._add_discard_events(
                    events=events, action_client=action_client, new_tile=new_tile
                )
        else:
            next_player_id = 0 if 2 < last_event.player_id else last_event.player_id + 1
            action_client = self.clients[next_player_id]
            events = self._add_discard_events(events=events, action_client=action_client, new_tile=new_tile)
            events = self._add_agari_events(events=events, action_client=action_client, new_tile=new_tile)
        player = action_client.to_player_observation(new_tile)
        clients = self.clients
        clients.remove(action_client)
        players = [client.to_player_observation(None) for client in clients] + [player]
        _observation = Observation(
            player=player,
            players=players,
            dealer_seat=self.dealer_seat,
            count_of_riichi_sticks=self.count_of_riichi_sticks,
            count_of_honba_sticks=self.count_of_honba_sticks,
            events=self.selected_events
        )
        return _observation, events, action_client

    def _add_discard_events(self, events: List[Event], action_client=GameClient, new_tile=int) -> List[Event]:
        discard_events = [
            DiscardEvent(player_id=action_client.id, discard_tile=discard_tile)
            for discard_tile in action_client.tiles + [new_tile]
        ]
        return events + discard_events

    def _add_agari_events(self, events: List[Event], action_client=GameClient, new_tile=int) -> List[Event]:
        agari_events = []
        is_agari = self._is_agari(tiles=action_client.tiles + [new_tile], melds=action_client.melds)
        if is_agari:
            agari_events.append(TsumoEvent(player_id=action_client.id))
        return events + agari_events

    def _is_agari(self, tiles: List[int], melds: List[Meld]) -> bool:
        _melds = [TilesConverter.to_34_array(meld.tiles) for meld in melds]
        agari = Agari()
        return agari.is_agari(tiles=TilesConverter.to_34_array(tiles), melds=_melds)

    def _execute_action(self, client: GameClient, _observation: Observation, selected_event: Event) -> bool:
        if isinstance(selected_event, DiscardEvent):
            return self._execute_discard(client=client, _observation=_observation, selected_event=selected_event)
        elif isinstance(selected_event, RiichiEvent):
            return self._execute_riichi(client=client, _observation=_observation, selected_event=selected_event)
        elif isinstance(selected_event, PonEvent):
            return self._execute_pon(client=client, selected_event=selected_event)
        elif isinstance(selected_event, ChiEvent):
            return self._execute_chi(client=client, selected_event=selected_event)
        elif isinstance(selected_event, AnKanEvent):
            return self._execute_an_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, MinKanEvent):
            return self._execute_min_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, KaKanEvent):
            return self._execute_ka_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, TsumoEvent):
            return self._execute_tsumo()
        elif isinstance(selected_event, RonEvent):
            return self._execute_ron()
        elif isinstance(selected_event, ChanKanEvent):
            return self._execute_chan_kan(client=client, selected_event=selected_event)
        elif isinstance(selected_event, KyushuKyuhaiEvent):
            return self._execute_kyushu_kyuhai(client=client, selected_event=selected_event)
        elif isinstance(selected_event, NoneEvent):
            return False
        else:
            raise 'NotFoundEvent'

    def _execute_discard(self, client: GameClient, _observation: Observation, selected_event: Event) -> bool:
        self._discard(client=client, _observation=_observation, selected_event=selected_event)
        return False

    def _discard(self, client: GameClient, _observation: Observation, selected_event: Event):
        if _observation.player.new_tile == selected_event.discard_tile:
            client.tiles = _observation.player.tiles
        elif selected_event.discard_tile in _observation.player.tiles:
            tiles = _observation.player.tiles
            tiles.remove(selected_event.discard_tile)
            tiles.append(_observation.player.new_tile)
            client.tiles = tiles
        else:
            raise 'NotFoundDiscardTile'

    def _execute_riichi(self, client: GameClient, _observation: Observation, selected_event: Event) -> bool:
        if len([client for client in self.clients if client.in_riichi]) == 3:
            return True
        client.in_riichi = True
        self._discard(client=client, _observation=_observation, selected_event=selected_event)
        self.count_of_honba_sticks += 1
        client.scores += 1000
        return False

    def _execute_pon(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def _execute_chi(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def _execute_an_kan(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def _execute_min_kan(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def _execute_ka_kan(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def _execute_tsumo(self) -> bool:
        return True

    def _execute_ron(self) -> bool:
        return True

    def _execute_chan_kan(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def _execute_kyushu_kyuhai(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def _execute_none(self, client: GameClient, selected_event: Event) -> bool:
        return False

    def next_round(self) -> bool:
        """
        next_actionがFalseを返すとroundが終わっているので、このメソッドを呼んで次のroundを始めてください
        Trueが返る間はroundが続いており、Falseが返るとgameが終了します
        """
        if self.ended_game:
            return False
        scores = self._calc_scores()
        next_dealer_seat = self._get_next_dealer_seat()
        self._update_ended_game(next_dealer_seat=next_dealer_seat)
        if self.ended_game:
            return False
        self._init_round(scores=scores, dealer_seat=next_dealer_seat)
        return not self.ended_game

    @property
    def clients(self) -> List[GameClient]:
        return [self.client0, self.client1, self.client2, self.client3]

    @property
    def dora_indicators(self) -> List[int]:
        if self.is_aka:
            return [self.wanpai[idx] for idx in self.dora_indexes] + AKA_DORA_LIST
        else:
            return [self.wanpai[idx] for idx in self.dora_indexes]

    @property
    def round_wind(self):
        if self.round_number < 4:
            return EAST
        elif 4 <= self.round_number < 8:
            return SOUTH
        elif 8 <= self.round_number < 12:
            return WEST
        else:
            return NORTH

    def _init_round(
        self,
        round_number=0,
        count_of_riichi_sticks=0,
        count_of_honba_sticks=0,
        dealer_seat=0,
        seats=[0, 1, 2, 3],
        scores=[25000, 25000, 25000, 25000],
    ):
        self.round_number = round_number
        self.count_of_riichi_sticks = count_of_riichi_sticks
        self.count_of_honba_sticks = count_of_honba_sticks
        self.dealer_seat = dealer_seat

        self.selected_events = []

        self.dora_indexes = [0]

        self._init_riichi()
        self._set_seats(seats)
        self._set_scores(scores)

        self._set_yama()
        self._haipai()

    def _init_riichi(self):
        for client in self.clients:
            client.in_riichi = False

    def _set_seats(self, seats=[0, 1, 2, 3]):
        for (i, client) in enumerate(self.clients):
            client.seat = seats[i]

    def _set_scores(self, scores=[25000, 25000, 25000, 25000]):
        for (i, client) in enumerate(self.clients):
            client.scores = scores[i]

    def _set_yama(self):
        hais = list(range(135))
        random.shuffle(hais)
        self.rinshanhai = hais[0:4]
        self.wanpai = hais[4:14]
        self.yama = hais[14:]

    def _haipai(self):
        for (i, client) in enumerate(self.clients):
            client.tiles = self.yama[i * 13:(i + 1) * 13]
        self.yama = self.yama[52:]

    def _get_next_dealer_seat(self) -> int:
        return self.dealer_seat + 1 if self.dealer_seat < 3 else 0

    def _calc_scores(self):
        scores = [client.scores for client in self.clients]
        hand = FinishedHand()
        for client in sorted(self.clients, key=lambda x: x.seat):
            client_events = [event for event in self.selected_events if event.player_id == client.id]
            win_event = client_events[-1] if len(client_events) > 0 else None
            if win_event is None or (not win_event.is_agari):
                next
            last_event = next((event for event in reversed(self.selected_events) if not event.is_agari), None)
            if last_event is None:
                raise 'NotFoundLastEvent'
            if last_event.discard_tile is None:
                raise 'NotFoundLastEventDiscardTile'

            res = hand.estimate_hand_value(
                tiles=client.tiles + [last_event.discard_tile],
                win_tile=last_event.discard_tile,
                is_tsumo=win_event.type == 'tsumo',
                is_riichi=client.in_riichi,
                is_dealer=client.seat == self.dealer_seat,
                is_ippatsu=last_event.player_id == client.id and last_event.type == 'riichi',
                is_rinshan=False,
                is_chankan=win_event.type == 'chan_kan',
                is_haitei=False,
                is_houtei=False,
                is_daburu_riichi=False,
                is_nagashi_mangan=False,
                is_tenhou=False,
                is_renhou=False,
                is_chiihou=False,
                open_sets=None,
                dora_indicators=self.dora_indicators,
                called_kan_indices=None,
                player_wind=GameClient.player_wind(self.dealer_seat),
                round_wind=self.round_wind,
            )

            if res['cost'] is not None:
                if win_event.type == 'ron':
                    scores[win_event.player_id] += res['cost']['main']
                    scores[last_event.player_id] -= res['cost']['main']
                elif win_event.type == 'tsumo':
                    for client in self.clients:
                        if client.id == win_event.player_id:
                            scores[client.id] += (3 * res['cost']['main']) + res['cost']['additional']
                        elif client.seat == self.dealer_seat:
                            scores[client.id] -= (res['cost']['main'] + res['cost']['additional'])
                        else:
                            scores[client.id] -= res['cost']['main']
        return scores

    def _update_ended_game(self, next_dealer_seat=0):
        self.round_number += 1
        self.ended_game = self.round_number == 8
