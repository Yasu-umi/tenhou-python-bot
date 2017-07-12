from game.table import GameTable
from mahjong.tile import TilesConverter

import datetime

if __name__ == '__main__':
    agari_occred = False
    start = datetime.datetime.now().timestamp()
    i = 1

    while True:
        t = GameTable()
        res = t.next_action()
        while res:
            res = t.next_action()
        for client in t.clients:
            print("id: {}, tiles: {}".format(client.id, TilesConverter.to_one_line_string(client.tiles)))
        t.next_round()
        for client in t.clients:
            if client.scores != 25000:
                agari_occred = True
        i += 1
        if i % 100 == 0:
            dif = datetime.datetime.now().timestamp() - start
            print("{} end round {}sec".format(i, dif))

        if agari_occred:
            dif = datetime.datetime.now().timestamp() - start
            print("{} end round {}sec".format(i, dif))
            for event in t.selected_events:
                print(event)
            for client in t.clients:
                print("id: {}, scores: {}".format(client.id, client.scores))
            agari_occred = False
