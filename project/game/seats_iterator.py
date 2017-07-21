# -*- coding: utf-8 -*-
from typing import List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.client import GameClient  # noqa


class SeatsIterator:
    def __init__(self, clients: List['GameClient']) -> None:
        self.clients = clients

    def __iter__(self) -> 'SeatsIterator':
        self.current_seat = 0
        return self

    def __next__(self) -> Optional['GameClient']:
        self.current_seat = self.current_seat + 1 if self.current_seat < 3 else 0
        client = next(filter(lambda x: x.seat == self.current_seat, self.clients), None)
        return client
