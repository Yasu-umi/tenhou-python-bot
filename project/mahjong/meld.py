# -*- coding: utf-8 -*-
from typing import List, Optional, TypeVar, Generic, Union, NewType

from mahjong.tile import TilesConverter

P = TypeVar('P')
CHI_TYPE = NewType('CHI_TYPE', str)
PON_TYPE = NewType('PON_TYPE', str)
KAN_TYPE = NewType('KAN_TYPE', str)
CHANKAN_TYPE = NewType('CHANKAN_TYPE', str)
NUKI_TYPE = NewType('NUKI_TYPE', str)
TYPE = Union[CHI_TYPE, PON_TYPE, KAN_TYPE, CHANKAN_TYPE, NUKI_TYPE]

class Meld(Generic[P]):
    CHI: 'CHI_TYPE' = CHI_TYPE('chi')
    PON: 'PON_TYPE' = PON_TYPE('pon')
    KAN: 'KAN_TYPE' = KAN_TYPE('kan')
    CHANKAN: 'CHANKAN_TYPE' = CHANKAN_TYPE('chankan')
    NUKI: 'NUKI_TYPE' = NUKI_TYPE('nuki')

    who: Optional[P] = None
    tiles: List[int] = []
    type: TYPE
    from_who: Optional[P] = None
    called_tile: int
    # we need it to distinguish opened and closed kan
    opened: bool = True

    def __init__(
        self,
        type: TYPE,
        tiles: List[int],
        called_tile: int,
        who: Optional[P] = None,
        from_who: Optional[P] = None,
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
