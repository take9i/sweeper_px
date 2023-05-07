#!/usr/bin/env python
import pyxel

# %%
AROUNDS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
UNIT = 8


# %%
class Game:
    def __init__(self):
        # pyxel.init(160, 120, "Game", 10)
        pyxel.init(240, 128, "Game", 10)
        pyxel.load("my_resource.pyxres")

        self.width = 30
        self.height = 16
        self.minemap = [[0] * self.width for j in range(self.height)]
        self.checkmap = [[False] * self.width for j in range(self.height)]
        self.flags = []
        rest = 99
        while rest > 0:
            x, y = pyxel.rndi(0, self.width - 1), pyxel.rndi(0, self.height - 1)
            if self.minemap[y][x] != 9:
                self.minemap[y][x] = 9
                rest -= 1
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.minemap[y][x] == 9:
                    continue
                x1, x2 = max(x - 1, 0), min(x + 2, self.width)
                y1, y2 = max(y - 1, 0), min(y + 2, self.height)
                self.minemap[y][x] = sum(
                    [
                        1 if self.minemap[j][i] == 9 else 0
                        for j in range(y1, y2)
                        for i in range(x1, x2)
                    ]
                )
        while True:
            x, y = pyxel.rndi(0, self.width - 1), pyxel.rndi(0, self.height - 1)
            if self.minemap[y][x] == 0:
                self.player = (x, y)
                self.open(x, y)
                break

        pyxel.run(self.update, self.draw)

    def confirm(self, x, y):
        unchecks = []
        for dx, dy in AROUNDS:
            xx, yy = x + dx, y + dy
            if (
                0 <= xx < self.width
                and 0 <= yy < self.height
                and not self.checkmap[yy][xx]
            ):
                unchecks.append((xx, yy))
        flags = [(x, y) for (x, y) in unchecks if (x, y) in self.flags]
        if len(unchecks) == self.minemap[y][x]:
            for x, y in unchecks:
                self.flags.append((x, y))
        elif len(flags) == self.minemap[y][x]:
            for x, y in unchecks:
                if (x, y) not in self.flags:
                    self.open(x, y)

    def open(self, x, y):
        self.checkmap[y][x] = True
        if self.minemap[y][x] != 0:
            return
        tracks = [(x, y)]
        while tracks:
            (x, y) = tracks.pop()
            for dx, dy in AROUNDS:
                xx, yy = x + dx, y + dy
                if (
                    0 <= xx < self.width
                    and 0 <= yy < self.height
                    and not self.checkmap[yy][xx]
                ):
                    self.checkmap[yy][xx] = True
                    if self.minemap[yy][xx] == 0:
                        tracks.append((xx, yy))

    def update(self):
        x, y = self.player
        if pyxel.btn(pyxel.KEY_Z):
            self.confirm(x, y)
            return
        if pyxel.btn(pyxel.KEY_LEFT):
            x -= 1
        elif pyxel.btn(pyxel.KEY_RIGHT):
            x += 1
        elif pyxel.btn(pyxel.KEY_UP):
            y -= 1
        elif pyxel.btn(pyxel.KEY_DOWN):
            y += 1
        x = min(max(x, 0), self.width - 1)
        y = min(max(y, 0), self.height - 1)
        if x == self.player[0] and y == self.player[1]:
            return
        if (x, y) in self.flags:
            return
        if not self.checkmap[y][x]:
            return

        self.open(x, y)
        self.player = (x, y)

    def draw(self):
        pyxel.cls(0)
        for y in range(0, self.height):
            for x in range(0, self.width):
                xx, yy = x * UNIT, y * UNIT
                if self.checkmap[y][x]:
                    pyxel.blt(xx, yy, 0, 8, 0, UNIT, UNIT)
                else:
                    pyxel.blt(xx, yy, 0, 0, 0, UNIT, UNIT)
        for y in range(0, self.height):
            for x in range(0, self.width):
                if not self.checkmap[y][x]:
                    continue
                xx, yy = x * UNIT, y * UNIT
                a = self.minemap[y][x]
                if a == 9:
                    pyxel.blt(xx, yy, 0, 16, 0, UNIT, UNIT, 0)
                elif a > 0:
                    pyxel.blt(xx, yy, 0, (a - 1) * UNIT, 8, UNIT, UNIT, 0)
        for x, y in self.flags:
            xx, yy = x * UNIT, y * UNIT
            pyxel.blt(xx, yy, 0, 24, 0, UNIT, UNIT, 0)
        xx, yy = self.player[0] * UNIT, self.player[1] * UNIT
        pyxel.blt(xx, yy, 0, 32, 0, UNIT, UNIT, 0)


if __name__ == "__main__":
    Game()
