# -*- coding: utf-8 -*-
import random
from typing import List

from client import ClientInterface, GameClient


class GameTable(object):
    round_number = 0
    count_of_honba_sticks = 0
    dealer_seat = 0

    rinshanhai = []  # type: List[int]
    wanpai = []  # type: List[int]
    yama = []  # type: List[int]

    dora_indexes = [0]  # type: List[int]

    end_round = False
    end_game = False

    def __init__(
        self,
        client1=ClientInterface,
        client2=ClientInterface,
        client3=ClientInterface,
        client4=ClientInterface,
        is_hanchan=True,
        is_open_tanyao=True,
        is_aka=True,
    ):
        self.client1 = GameClient(client1)
        self.client2 = GameClient(client2)
        self.client3 = GameClient(client3)
        self.client4 = GameClient(client4)

        self.is_hanchan = is_hanchan
        self.is_open_tanyao = is_open_tanyao
        self.is_aka = is_aka

        self._init_round()

    def next_action(self) -> bool:
        """
        GameTableの初期化後このメソッドを呼んでください
        Trueが返る間はroundが続いており、next_actionを呼ぶ事でゲームが進みます
        """
        if self.end_round:
            return False
        return True

    def next_round(self) -> bool:
        """
        next_actionがFalseを返すとroundが終わっているので、このメソッドを呼んで次のroundを始めてください
        Trueが返る間はroundが続いており、Falseが返るとgameが終了します
        """
        if self.end_game:
            return False
        return True

    @property
    def clients(self) -> List[GameClient]:
        return [self.client1, self.client2, self.client3, self.client4]

    def _init_round(
        self,
        round_number=0,
        count_of_honba_sticks=0,
        dealer_seat=0,
        scores=[25000, 25000, 25000, 25000],
    ):
        self.round_number = round_number
        self.count_of_honba_sticks = count_of_honba_sticks
        self.dealer_seat = dealer_seat

        self.dora_indexes = [0]

        self._init_riichi()
        self._set_scores(scores)

        self._set_yama_and_wanpai()
        self._set_initial_seats()
        self._haipai()

    def _init_riichi(self):
        for client in self.clients:
            self.client.in_riichi = False

    def _set_scores(self, scores=[25000, 25000, 25000, 25000]):
        for (i, client) in enumerate(self.clients):
            self.client.scores = scores[i]

    def _set_yama_and_wanpai(self):
        hais = range(135)
        random.shuffle(hais)
        self.rinshanhai = hais[0:3]
        self.wanpai = hais[3:13]
        self.yama = hais[13:]

    def _set_initial_seats(self):
        seats = random.shuffle(range(4))
        for (i, client) in enumerate(self.clients):
            self.client.seat = seats[i]

    def _haipai(self):
        for (i, client) in enumerate(self.clients):
            client.tiles = self.yama[i * 13:(i + 1) * 13]
        self.yama = self.yama[52:]
