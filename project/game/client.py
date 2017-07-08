# -*- coding: utf-8 -*-
import random
from typing import List

from .event import Event
from .observation import Observation


class ClientInterface(object):
    def action(
      self,
      events: List[Event],
      observation: Observation
    ) -> Event:
        return random.choice(events)
