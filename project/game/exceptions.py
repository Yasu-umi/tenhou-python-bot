# -*- coding: utf-8 -*-


class ThisRoundAlreadyEndsException(Exception):
    pass


class NotFoundLastEventException(Exception):
    pass


class NotFoundLastEventDiscardTileException(Exception):
    pass


class NotFoundNewTileException(Exception):
    pass


class NotFoundDiscardTileException(Exception):
    pass


class NotFromWhoException(Exception):
    pass


class NotFoundNextSeatPlayerException(Exception):
    pass
