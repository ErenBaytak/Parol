#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parol Repair - Terminal (curses) arayuzu
Copyright (C) 2026 Ermedsoft - Eren Baytak Yazılım
GNU GPL v3 or later. Bu program HICBIR GARANTI icermez.
"""
import curses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import parol_common as C  # noqa: E402

MIN_Y, MIN_X = 24, 80


class TUI:
    def __init__(self, scr):
        self.scr = scr
        self.sel = 0
        self.off = 0
        self.cat = None
        self.csel = 0
        self.coff = 0

    # -------------------------------------------------------------- kurulum
    def setup(self):
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        yellow, magenta = curses.COLOR_YELLOW, curses.COLOR_MAGENTA
        if curses.can_change_color() and curses.COLORS >= 256:
            try:
                curses.init_color(220, 1000, 871, 349)   # #ffde59
                curses.init_color(198, 1000, 0, 498)     # #ff007f
                yellow, magenta = 220, 198
            except curses.error:
                pass
        curses.init_pair(1, yellow, bg)
        curses.init_pair(2, magenta, bg)
        curses.init_pair(3, curses.COLOR_WHITE, bg)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        self.scr.keypad(True)
        self.scr.timeout(200)

    def y(self):
        return curses.color_pair(1)

    def m(self):
        return curses.color_pair(2)

    def w(self):
        return curses.color_pair(3)

    # ------------------------------------------------------------ cizim primitives
    def put(self, row, col, text, attr=0):
        height, width = self.scr.getmaxyx()
        if row < 0 or row >= height or col < 0 or col >= width:
            return
        text = C.ascii_tr(text)[: max(0, width - col - 1)]
        try:
            self.scr.addstr(row, col, text, attr)
        except curses.error:
            pass

    def center(self, row, text, attr=0):
        width = self.scr.getmaxyx()[1]
        text = C.ascii_tr(text)
        self.put(row, max(0, (width - len(text)) // 2), text, attr)

    def header(self):
        self.scr.erase()
        width = self.scr.getmaxyx()[1]
        self.put(0, 0, "=" * (width - 1), self.y())
        self.center(1, "PAROL REPAIR v" + C.VERSION, self.y() | curses.A_BOLD)
        self.center(2, C.t("tui_sub"), self.m())
        self.put(3, 0, "=" * (width - 1), self.y())

    def footer(self, nav_key):
        height, width = self.scr.getmaxyx()
        base = height - 5
        self.center(base, C.t(nav_key), self.y())
        self.center(base + 1, C.t("version_line"), self.y())
        self.center(base + 2, C.COPYRIGHT, self.y() | curses.A_BOLD)
        self.center(base + 3, C.t("license"), self.m())
        self.put(height - 1, 0, "=" * (width - 1), self.y())

    def body_height(self):
        return max(1, self.scr.getmaxyx()[0] - 5 - 7)

    def draw_list(self, items, sel, off, top):
        height = self.body_height()
        total = len(items)
        if sel < off:
            off = sel
        elif sel >= off + height:
            off = sel - height + 1
        off = max(0, min(off, max(0, total - height)))
        width = self.scr.getmaxyx()[1]
        left = max(2, (width - 74) // 2)
        for i in range(height):
            idx = off + i
            if idx >= total:
                break
            label, hot = items[idx]
            row = top + i
            mark = ">" if idx == sel else " "
            attr = (self.m() | curses.A_BOLD) if idx == sel else (self.w() if not hot else self.y())
            self.put(row, left, "%s %2d. %s" % (mark, idx + 1, label), attr)
        if total > height:
            info = "[%d-%d/%d]" % (off + 1, min(off + height, total), total)
            self.put(top - 1, width - len(info) - 2, info, self.y())
        return off

    # --------------------------------------------------------------- ekranlar
    def main_items(self):
        items = [("[%s] %s" % (c["icon"], C.cname(c)), False) for c in C.CATALOG]
        items.append(("[ALL] " + C.t("auto") + " - " + C.t("auto_desc"), True))
        items.append(("[LOG] " + C.t("view_log"), False))
        items.append(("[EXT] " + C.t("exit"), False))
        return items

    def cat_items(self, cat):
        items = [("%s  [%s]" % (C.adesc(a), C.risk_label(a)), False) for a in cat["actions"]]
        items.append((C.t("run_cat"), True))
        items.append((C.t("back"), False))
        return items

    def message(self, title, text, bad=False):
        self.scr.erase()
        self.center(2, title, (self.m() if bad else self.y()) | curses.A_BOLD)
        row = 5
        for line in C.ascii_tr(text).split("\n"):
            if row >= self.scr.getmaxyx()[0] - 6:
                break
            self.center(row, line, self.w())
            row += 1
        self.center(self.scr.getmaxyx()[0] - 6, C.t("press"), self.y())
        self.scr.refresh()
        self.scr.timeout(-1)
        self.scr.getch()
        self.scr.timeout(200)

    def output_view(self, title, body, status):
        self.scr.erase()
        height, width = self.scr.getmaxyx()
        color = self.y() if status == "ok" else self.m()
        self.put(1, 2, "%s  [%s]" % (C.ascii_tr(title), C.t(status)), color | curses.A_BOLD)
        self.put(2, 2, "-" * (width - 5), self.y())
        lines = C.ascii_tr(body).split("\n")
        room = height - 9
        for i, line in enumerate(lines[-room:]):
            self.put(4 + i, 2, line[: width - 5], self.w())
        self.put(height - 6, 2, C.t("press"), self.y())
        self.scr.refresh()
        self.scr.timeout(-1)
        self.scr.getch()
        self.scr.timeout(200)

    def confirm(self, act):
        if act["risk"] != "high":
            return True
        self.scr.erase()
        self.center(2, C.t("confirm"), self.m() | curses.A_BOLD)
        self.center(5, C.t("high"), self.w())
        self.center(7, C.adesc(act), self.y() | curses.A_BOLD)
        self.center(9, C.t("ask") + "  (e/y = OK, diger = " + C.t("exit") + ")", self.w())
        self.scr.refresh()
        self.scr.timeout(-1)
        key = self.scr.getch()
        self.scr.timeout(200)
        return key in (ord("e"), ord("E"), ord("y"), ord("Y"))

    def run_one(self, act):
        if not self.confirm(act):
            return
        self.scr.erase()
        self.center(3, C.t("running") + ": " + C.adesc(act), self.y() | curses.A_BOLD)
        self.center(5, C.t("wait"), self.w())
        self.scr.refresh()
        status, body = C.execute(act)
        C.log("%s -> %s" % (C.adesc(act), status), "INFO" if status == "ok" else "WARN")
        self.output_view(C.adesc(act), body, status)

    def run_many(self, pairs, title):
        total = len(pairs)
        ok = 0
        skipped = 0
        for idx, (cat, act) in enumerate(pairs, start=1):
            self.scr.erase()
            height, width = self.scr.getmaxyx()
            self.put(1, 2, "%s  [%d/%d]" % (C.ascii_tr(title), idx, total), self.m() | curses.A_BOLD)
            self.put(2, 2, "%s > %s" % (C.ascii_tr(C.cname(cat)), C.ascii_tr(C.adesc(act))), self.y())
            self.put(3, 2, "-" * (width - 5), self.y())
            bar_w = max(10, width - 12)
            filled = int(idx / total * bar_w)
            self.put(5, 2, "[" + "#" * filled + "-" * (bar_w - filled) + "]", self.y())
            self.put(7, 2, C.t("wait"), self.w())
            self.put(height - 6, 2, "ESC/Q = " + C.t("exit"), self.m())
            self.scr.refresh()
            status, body = C.execute(act)
            if status == "ok":
                ok += 1
            elif status == "skip":
                skipped += 1
            C.log("%s :: %s -> %s" % (C.cname(cat), C.adesc(act), status),
                  "INFO" if status == "ok" else "WARN")
            self.scr.nodelay(True)
            key = self.scr.getch()
            self.scr.nodelay(False)
            if key in (27, ord("q"), ord("Q")):
                self.message(C.t("abort"), "%s: %d/%d" % (C.t("success"), ok, total), bad=True)
                return
        self.message(C.t("done"),
                     "%s: %d/%d\n%s: %d\n\n%s: %s" %
                     (C.t("success"), ok, total, C.t("skip"), skipped, C.t("details"), C.LOG_FILE))

    def show_log(self):
        try:
            with open(C.LOG_FILE, "r", encoding="utf-8", errors="replace") as fh:
                body = "".join(fh.readlines()[-200:]) or C.t("log_empty")
        except OSError:
            body = C.t("log_empty")
        self.output_view(C.t("view_log"), body, "ok")

    # ------------------------------------------------------------------ dongu
    def loop(self):
        self.setup()
        while True:
            height, width = self.scr.getmaxyx()
            if height < MIN_Y or width < MIN_X:
                self.scr.erase()
                self.put(0, 0, C.t("small"), self.m() | curses.A_BOLD)
                self.put(1, 0, "%dx%d -> %dx%d" % (width, height, MIN_X, MIN_Y), self.w())
                self.put(3, 0, "ESC/Q", self.y())
                self.scr.refresh()
                key = self.scr.getch()
                if key in (27, ord("q"), ord("Q")):
                    return
                continue

            self.header()
            if self.cat is None:
                items = self.main_items()
                self.center(5, C.t("select_cat"), self.w() | curses.A_BOLD)
                self.off = self.draw_list(items, self.sel, self.off, 7)
                self.footer("nav_main")
            else:
                cat = self.cat
                self.put(5, 2, "[%s] %s" % (cat["icon"], C.cname(cat)), self.m() | curses.A_BOLD)
                self.put(6, 2, C.cdesc(cat), self.y())
                items = self.cat_items(cat)
                self.coff = self.draw_list(items, self.csel, self.coff, 8)
                self.footer("nav_cat")
            self.scr.refresh()
            key = self.scr.getch()
            if key in (-1, curses.KEY_RESIZE):
                continue

            if self.cat is None:
                ncat = len(C.CATALOG)
                total = ncat + 3
                if key == curses.KEY_UP:
                    self.sel = (self.sel - 1) % total
                elif key == curses.KEY_DOWN:
                    self.sel = (self.sel + 1) % total
                elif key == curses.KEY_PPAGE:
                    self.sel = max(0, self.sel - self.body_height())
                elif key == curses.KEY_NPAGE:
                    self.sel = min(total - 1, self.sel + self.body_height())
                elif key == curses.KEY_HOME:
                    self.sel = 0
                elif key == curses.KEY_END:
                    self.sel = total - 1
                elif key in (10, 13, curses.KEY_ENTER):
                    if self.sel < ncat:
                        self.cat = C.CATALOG[self.sel]
                        self.csel = self.coff = 0
                    elif self.sel == ncat:
                        self.run_many(C.auto_actions(), C.t("auto"))
                    elif self.sel == ncat + 1:
                        self.show_log()
                    else:
                        return
                elif key in (27, ord("q"), ord("Q")):
                    return
                elif ord("1") <= key <= ord("9"):
                    pick = key - ord("1")
                    if pick < total:
                        self.sel = pick
            else:
                acts = self.cat["actions"]
                total = len(acts) + 2
                if key == curses.KEY_UP:
                    self.csel = (self.csel - 1) % total
                elif key == curses.KEY_DOWN:
                    self.csel = (self.csel + 1) % total
                elif key in (ord("b"), ord("B"), 27):
                    self.cat = None
                elif key in (ord("q"), ord("Q")):
                    return
                elif key in (10, 13, curses.KEY_ENTER):
                    if self.csel < len(acts):
                        self.run_one(acts[self.csel])
                    elif self.csel == len(acts):
                        pairs = [(self.cat, a) for a in C.safe_actions(self.cat)]
                        self.run_many(pairs, C.cname(self.cat))
                    else:
                        self.cat = None
                elif ord("1") <= key <= ord("9"):
                    pick = key - ord("1")
                    if pick < total:
                        self.csel = pick


def main():
    if "--version" in sys.argv:
        print("%s %s - %s" % (C.APP_NAME, C.VERSION, C.COPYRIGHT))
        return 0
    if not C.is_root():
        print(C.t("root_needed"))
        return 1
    C.log("Terminal arayuzu baslatildi (lang=%s)" % C.LANG)
    try:
        curses.wrapper(lambda scr: TUI(scr).loop())
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
