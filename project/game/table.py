# -*- coding: utf-8 -*-
import random
from typing import List

from game.action_excutor import ActionExcutor
from game.arguments_creator import ArgumentsCreator
from game.client import ClientInterface, BaseClient, GameClient
from game.exceptions import NotFoundLastEventException, NotFoundLastEventDiscardTileException
from game.event import (PonEvent, ChiEvent, AnKanDeclarationEvent, MinKanDeclarationEvent, KaKanDeclarationEvent,
                        TsumoEvent, RinshanTsumoEvent, RiichiEvent, TsumoAgariEvent, RonAgariEvent, ChanKanAgariEvent, KyushuKyuhaiEvent, NoneEvent,
                        Event)
from game.seats_iterator import SeatsIterator

from mahjong.constants import EAST, SOUTH, WEST, NORTH, AKA_DORA_LIST
from mahjong.hand import FinishedHand


class GameTable(object):
    round_number = 0
    count_of_riichi_sticks = 0
    count_of_honba_sticks = 0
    dealer_seat = 0

    selected_events:  List[Event] = []

    rinshanhai: List[int] = []
    wanpai: List[int] = []
    yama: List[int] = []

    n_open_dora: int = 0

    ended_round = False
    ended_game = False

    @property
    def clients(self) -> List['GameClient']:
        return [self.client0, self.client1, self.client2, self.client3]

    @property
    def clients_loop_iter_orderby_seat(self) -> 'SeatsIterator':
        return SeatsIterator(self.clients)

    @property
    def open_dora_indicators(self) -> List[int]:
        """
        王牌の中でオープンになっているドラ、(使用時のみ)赤ドラ
        """
        if self.is_aka:
            return list(set([self.wanpai[idx] for idx in range(0, self.n_open_dora)] + AKA_DORA_LIST))
        else:
            return [self.wanpai[idx] for idx in range(0, self.n_open_dora)]

    @property
    def all_dora_indicators(self) -> List[int]:
        """
        王牌の中でオープンになっているドラ、裏ドラ、(使用時のみ)赤ドラ
        """
        return list(set(self.open_dora_indicators + [self.wanpai[idx * 2] for idx in range(0, self.n_open_dora)]))

    @property
    def round_wind(self) -> int:
        if self.round_number < 4:
            return EAST
        elif 4 <= self.round_number < 8:
            return SOUTH
        elif 8 <= self.round_number < 12:
            return WEST
        else:
            return NORTH

    def __init__(
        self,
        client0: ClientInterface = BaseClient(),
        client1: ClientInterface = BaseClient(),
        client2: ClientInterface = BaseClient(),
        client3: ClientInterface = BaseClient(),
        is_hanchan: bool = True,
        is_open_tanyao: bool = True,
        is_aka: bool = True,
    ) -> None:
        self.client0 = GameClient(id=0, client=client0)
        self.client1 = GameClient(id=1, client=client1)
        self.client2 = GameClient(id=2, client=client2)
        self.client3 = GameClient(id=3, client=client3)

        self.is_hanchan = is_hanchan
        self.is_open_tanyao = is_open_tanyao
        self.is_aka = is_aka

        self._init_round()
    
    def clients_by_seat_range(start: int = 0, end: = 4):
        addFlag = False
        clients: List['GameClient'] = []
        for client in self.clients_loop_iter_orderby_seat:
            if client is None:
                raise NotFoundNextSeatPlayerException
            if client.seat == start:
                addFlag = True
            if client.seat == end - 1:
                addFlag = False
                break
            if addFlag:
                clients.append(client)
        return clients

    def next_action(self) -> bool:
        """
        GameTableの初期化後このメソッドを呼んでください
        Trueが返る間はroundが続いており、next_actionを呼ぶ事でゲームが進みます
        """
        self._update_ended_round()
        if self.ended_round:
            return False

        _observation, events, client = ArgumentsCreator.create(table=self)

        selected_event = client.action(_observation=_observation, events=events)
        self.selected_events.append(selected_event)

        self.ended_round = ActionExcutor.execute_action(
            table=self,
            client=client,
            _observation=_observation,
            selected_event=selected_event,
        )

        return not self.ended_round

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

    def _init_round(
        self,
        round_number: int = 0,
        count_of_riichi_sticks: int = 0,
        count_of_honba_sticks: int = 0,
        dealer_seat: int = 0,
        seats: List[int] = [0, 1, 2, 3],
        scores: List[int] = [25000, 25000, 25000, 25000],
    ) -> None:
        self.round_number = round_number
        self.count_of_riichi_sticks = count_of_riichi_sticks
        self.count_of_honba_sticks = count_of_honba_sticks
        self.dealer_seat = dealer_seat

        self.selected_events = []

        self.n_open_dora = 1

        self._init_riichi()
        self._set_seats(seats)
        self._set_scores(scores)

        self._set_yama()
        self._haipai()

    def _init_riichi(self) -> None:
        for client in self.clients:
            client.in_riichi = False

    def _set_seats(self, seats: List[int] = [0, 1, 2, 3]) -> None:
        for (i, client) in enumerate(self.clients):
            client.seat = seats[i]

    def _set_scores(self, scores: List[int] = [25000, 25000, 25000, 25000]) -> None:
        for (i, client) in enumerate(self.clients):
            client.scores = scores[i]

    def _set_yama(self) -> None:
        hais = list(range(135))
        random.shuffle(hais)
        self.rinshanhai = hais[0:4]
        self.wanpai = hais[4:14]
        self.yama = hais[14:]

    def _haipai(self) -> None:
        for (i, client) in enumerate(self.clients):
            client.tiles = self.yama[i * 13:(i + 1) * 13]
        self.yama = self.yama[52:]

    def _update_ended_round(self) -> None:
        last_event = self.selected_events[-1] if len(self.selected_events) > 0 else None
        if len(self.yama) == 0 or (last_event is not None and last_event.is_agari):
            self.ended_round = True

    def _get_next_dealer_seat(self) -> int:
        return self.dealer_seat + 1 if self.dealer_seat < 3 else 0

    def _calc_scores(self) -> List[int]:
        scores = [client.scores for client in self.clients]
        hand = FinishedHand()
        for client in sorted(self.clients, key=lambda x: x.seat):
            client_events = [event for event in self.selected_events if event.player_id == client.id]
            win_event = client_events[-1] if len(client_events) > 0 else None
            if win_event is None or (not win_event.is_agari):
                next
            last_event = next((event for event in reversed(self.selected_events) if not event.is_agari), None)
            if last_event is None:
                raise NotFoundLastEventException
            if last_event.discard_tile is None:
                raise NotFoundLastEventDiscardTileException

            res = hand.estimate_hand_value(
                tiles=client.tiles + [last_event.discard_tile],
                win_tile=last_event.discard_tile,
                is_tsumo=isinstance(win_event, TsumoAgariEvent),
                is_riichi=client.in_riichi,
                is_dealer=client.seat == self.dealer_seat,
                is_ippatsu=last_event.player_id == client.id and isinstance(last_event, RiichiEvent),
                is_rinshan=False,
                is_chankan=isinstance(win_event, ChanKanAgariEvent),
                is_haitei=False,
                is_houtei=False,
                is_daburu_riichi=False,
                is_nagashi_mangan=False,
                is_tenhou=False,
                is_renhou=False,
                is_chiihou=False,
                open_sets=None,
                dora_indicators=self.all_dora_indicators,
                called_kan_indices=None,
                player_wind=GameClient.player_wind(self.dealer_seat),
                round_wind=self.round_wind,
            )

            if res['cost'] is not None:
                if isinstance(win_event, RonAgariEvent):
                    scores[win_event.player_id] += res['cost']['main']
                    scores[last_event.player_id] -= res['cost']['main']
                elif isinstance(win_event, TsumoAgariEvent):
                    for client in self.clients:
                        if client.id == win_event.player_id:
                            scores[client.id] += (3 * res['cost']['main']) + res['cost']['additional']
                        elif client.seat == self.dealer_seat:
                            scores[client.id] -= (res['cost']['main'] + res['cost']['additional'])
                        else:
                            scores[client.id] -= res['cost']['main']
        return scores

    def _update_ended_game(self, next_dealer_seat: int = 0) -> None:
        self.round_number += 1
        self.ended_game = self.round_number == 8
