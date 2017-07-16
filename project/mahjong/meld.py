# -*- coding: utf-8 -*-
from typing import List, Optional, TypeVar, Generic

from mahjong.tile import TilesConverter

P = TypeVar('P')

class Meld(Generic[P]):
    CHI = 'chi'
    PON = 'pon'
    KAN = 'kan'
    CHANKAN = 'chankan'
    NUKI = 'nuki'

    who: Optional[P] = None
    tiles: List[int] = []
    type: str = ''
    from_who: Optional[P] = None
    called_tile: int
    # we need it to distinguish opened and closed kan
    opened: bool = True

    def __init__(
        self,
        tiles: List[int],
        called_tile: int,
        who: Optional[P] = None,
        from_who: Optional[P] = None,
        type: str = '',
        opened: bool = True,
    ) -> None:
        self.who = who
        self.tiles = tiles
        self.type = type
        self.from_who = from_who
        self.called_tile = called_tile
        self.opened = opened

    def __str__(self) -> str:
        return 'Type: {}, Tiles: {} {}'.format(self.type, TilesConverter.to_one_line_string(self.tiles), self.tiles)

    # for calls in array
    def __repr__(self) -> str:
        return self.__str__()
