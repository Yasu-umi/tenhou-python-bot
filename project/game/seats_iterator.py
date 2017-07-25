# -*- coding: utf-8 -*-
from typing import List
from collections import Iterator

from game.exceptions import NotFoundNextSeatPlayerException

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.client import GameClient  # noqa


class SeatsIterator(Iterator):
    def __init__(self, clients: List['GameClient']) -> None:
        self.clients = clients

    def __iter__(self) -> 'SeatsIterator':
        self.current_seat = 0
        return self

    def __next__(self) -> 'GameClient':
        self.current_seat = (self.current_seat + 1) % 4
        client = next(filter(lambda x: x.seat == self.current_seat, self.clients), None)
        if client is None:
            raise NotFoundNextSeatPlayerException
        return client
