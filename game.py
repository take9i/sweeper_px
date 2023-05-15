#!/usr/bin/env python
import pyxel

SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2
AROUNDS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
UNIT = 8


# %%
class App:
    def __init__(self):
        # pyxel.init(160, 120, "Game", 10)
        pyxel.init(240, 128, "Game", 10)
        pyxel.load("my_resource.pyxres")
        self.scene = SCENE_TITLE
        pyxel.run(self.update, self.draw)

    def init_map(self):
        self.width = 30
        self.height = 16
        self.minemap = [[0] * self.width for j in range(self.height)]
        self.openedmap = [[False] * self.width for j in range(self.height)]
        self.flags = []
        self.surrounds = []
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

    def open(self, x, y):
        def open_domain(x, y):
            tracks = [(x, y)]
            while tracks:
                (x, y) = tracks.pop()
                for dx, dy in AROUNDS:
                    xx, yy = x + dx, y + dy
                    if (
                        0 <= xx < self.width
                        and 0 <= yy < self.height
                        and not self.openedmap[yy][xx]
                    ):
                        self.openedmap[yy][xx] = True
                        if self.minemap[yy][xx] == 0:
                            tracks.append((xx, yy))

        def open_mine():
            for y in range(0, self.height):
                for x in range(0, self.width):
                    if self.minemap[y][x] == 9 and (x, y) not in self.flags:
                        self.openedmap[y][x] = True

        self.openedmap[y][x] = True
        a = self.minemap[y][x]
        if a == 9:
            open_mine()
            self.scene = SCENE_GAMEOVER
        elif a == 0:
            open_domain(x, y)

    def check_surrounds(self, x, y):
        unopeneds = [
            (xx, yy)
            for dx, dy in AROUNDS
            if 0 <= (xx := self.player[0] + dx) < self.width
            and 0 <= (yy := self.player[1] + dy) < self.height
            and not self.openedmap[yy][xx]
        ]
        flags = [(x, y) for (x, y) in unopeneds if (x, y) in self.flags]
        if len(flags) == self.minemap[y][x]:
            for x, y in unopeneds:
                if (x, y) not in flags:
                    self.open(x, y)
        elif len(unopeneds) == self.minemap[y][x]:
            for x, y in unopeneds:
                self.flags.append((x, y))

    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_PLAY:
            self.update_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.update_gameover_scene()

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            self.init_map()
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        if pyxel.btn(pyxel.KEY_Z):
            self.surrounds = [
                (xx, yy)
                for dx, dy in AROUNDS
                if 0 <= (xx := self.player[0] + dx) < self.width
                and 0 <= (yy := self.player[1] + dy) < self.height
                and (xx, yy) not in self.flags
            ]
        elif pyxel.btnr(pyxel.KEY_Z):
            self.surrounds = []
            self.check_surrounds(self.player[0], self.player[1])
            return

        x, y = self.player
        if pyxel.btn(pyxel.KEY_LEFT):
            x -= 1 if 0 < x else 0
        elif pyxel.btn(pyxel.KEY_RIGHT):
            x += 1 if x < self.width - 1 else 0
        elif pyxel.btn(pyxel.KEY_UP):
            y -= 1 if 0 < y else 0
        elif pyxel.btn(pyxel.KEY_DOWN):
            y += 1 if y < self.height - 1 else 0
        if self.openedmap[y][x]:
            self.player = (x, y)
        elif (x, y) in self.surrounds:
            self.player = (x, y)
            self.open(x, y)

    def update_gameover_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            self.init_map()
            self.scene = SCENE_PLAY

    def draw(self):
        pyxel.cls(0)
        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.draw_gameover_scene()

    def draw_title_scene(self):
        pyxel.text(pyxel.width / 2 - 6 * 4, 40, "MINE SWEEPER", 7)
        pyxel.text(pyxel.width / 2 - 7.5 * 4, 96, "- PRESS ENTER -", 13)

    def draw_play_scene(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                xx, yy = x * UNIT, y * UNIT
                if self.openedmap[y][x] or (x, y) in self.surrounds:
                    pyxel.blt(xx, yy, 0, 8, 0, UNIT, UNIT)
                else:
                    pyxel.blt(xx, yy, 0, 0, 0, UNIT, UNIT)
                a = self.minemap[y][x]
                if 0 < a < 9 and self.openedmap[y][x]:
                    pyxel.blt(xx, yy, 0, (a - 1) * UNIT, 8, UNIT, UNIT, 0)
                elif (x, y) in self.flags:
                    pyxel.blt(xx, yy, 0, 16, 0, UNIT, UNIT, 0)
        xx, yy = self.player[0] * UNIT, self.player[1] * UNIT
        pyxel.blt(xx, yy, 0, 32, 0, UNIT, UNIT, 0)

    def draw_gameover_scene(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                xx, yy = x * UNIT, y * UNIT
                if self.openedmap[y][x]:
                    pyxel.blt(xx, yy, 0, 8, 0, UNIT, UNIT)
                else:
                    pyxel.blt(xx, yy, 0, 0, 0, UNIT, UNIT)
                a = self.minemap[y][x]
                if 0 < a < 9 and self.openedmap[y][x]:
                    pyxel.blt(xx, yy, 0, (a - 1) * UNIT, 8, UNIT, UNIT, 0)
                elif (x, y) in self.flags:
                    pyxel.blt(xx, yy, 0, 16, 0, UNIT, UNIT, 0)
                elif a == 9:
                    pyxel.blt(xx, yy, 0, 64, 8, UNIT, UNIT, 0)
        xx, yy = self.player[0] * UNIT, self.player[1] * UNIT
        pyxel.blt(xx, yy, 0, 40, 0, UNIT, UNIT, 0)


App()
