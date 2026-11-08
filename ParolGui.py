#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parol Repair - Recovery GUI (Windows Recovery tarzi, kernel panic pembesi)
Copyright (C) 2026 Ermedsoft - Eren Baytak Yazılım
GNU GPL v3 or later. Bu program HICBIR GARANTI icermez.
"""
import os
import subprocess
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import parol_common as C  # noqa: E402

try:
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import messagebox
except ImportError:
    print("python3-tk gerekli:  sudo apt install python3-tk")
    sys.exit(1)

BG      = "#ff007f"   # kernel panic pembesi
ACCENT  = "#ffde59"   # sari
SOFT    = "#ff4d9f"
TEXT    = "#ffffff"
DARK    = "#1a1a1a"


class Recovery:
    def __init__(self, root):
        self.root = root
        self.root.title("Parol Repair — Recovery")
        self.root.configure(bg=BG)
        self.root.geometry("1100x740")
        try:
            self.root.attributes("-fullscreen", True)
        except tk.TclError:
            pass

        self.fam = "Consolas"

        self.rows = []
        self.sel = 0
        self.busy = False
        self.back_cb = None
        self.canvas = None
        self.inner = None

        self.shell = tk.Frame(root, bg=BG)
        self.shell.pack(fill=tk.BOTH, expand=True, padx=70, pady=45)

        root.bind("<Up>", self.on_up)
        root.bind("<Down>", self.on_down)
        root.bind("<Return>", self.on_enter)
        root.bind("<Escape>", self.on_escape)
        root.bind("<F11>", lambda e: self.toggle_full())
        root.bind("<Button-4>", lambda e: self.wheel(-1))
        root.bind("<Button-5>", lambda e: self.wheel(1))
        root.bind("<MouseWheel>", lambda e: self.wheel(-1 if e.delta > 0 else 1))

        C.log("Recovery GUI baslatildi (lang=%s)" % C.LANG)
        self.screen_main()

    # ------------------------------------------------------------- yardimci
    def f(self, size, weight="normal"):
        return (self.fam, size, weight)

    def toggle_full(self):
        try:
            self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
        except tk.TclError:
            pass

    def clear(self):
        for w in self.shell.winfo_children():
            w.destroy()
        self.rows = []
        self.canvas = None
        self.inner = None

    def footer(self, nav=True):
        box = tk.Frame(self.shell, bg=BG)
        box.pack(side=tk.BOTTOM, fill=tk.X, pady=(14, 0))
        if nav:
            tk.Label(box, text=C.t("nav_gui"), font=self.f(10), fg=TEXT, bg=BG).pack()
        tk.Label(box, text=C.t("version_line"), font=self.f(10), fg=TEXT, bg=BG).pack(pady=(4, 0))
        tk.Label(box, text=C.COPYRIGHT, font=self.f(10, "bold"), fg=ACCENT, bg=BG).pack()
        tk.Label(box, text=C.t("license"), font=self.f(9), fg=TEXT, bg=BG).pack()

    def title(self, text, subtitle=None, size=42):
        tk.Label(self.shell, text=text, font=self.f(size, "bold"),
                 fg=TEXT, bg=BG, anchor="w", justify="left").pack(fill=tk.X, pady=(0, 8))
        if subtitle:
            tk.Label(self.shell, text=subtitle, font=self.f(13), fg=TEXT, bg=BG,
                     anchor="w", justify="left", wraplength=900).pack(fill=tk.X, pady=(0, 26))

    def menu(self, title, subtitle, items, back=None, size=42):
        """items: [(etiket, callback)]"""
        self.clear()
        self.busy = False
        self.sel = 0
        self.back_cb = back
        self.title(title, subtitle, size)

        holder = tk.Frame(self.shell, bg=BG)
        holder.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(holder, bg=BG, highlightthickness=0, bd=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.inner = tk.Frame(self.canvas, bg=BG)
        win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(win, width=e.width))
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        for idx, (label, cb) in enumerate(items):
            row = tk.Label(self.inner, text=label, font=self.f(16), anchor="w",
                           fg=TEXT, bg=BG, padx=26, pady=13, cursor="hand2")
            row.pack(fill=tk.X, pady=4)
            row.bind("<Button-1>", lambda e, c=cb: self.invoke(c))
            row.bind("<Enter>", lambda e, i=idx: self.hover(i))
            self.rows.append(row)

        self.paint()
        self.footer()

    def invoke(self, cb):
        if not self.busy and callable(cb):
            cb()

    def hover(self, idx):
        if not self.busy:
            self.sel = idx
            self.paint()

    def paint(self):
        for i, row in enumerate(self.rows):
            if i == self.sel:
                row.config(bg=ACCENT, fg=DARK)
            else:
                row.config(bg=BG, fg=TEXT)
        self.ensure_visible()

    def ensure_visible(self):
        if not self.rows or self.canvas is None:
            return
        self.canvas.update_idletasks()
        row = self.rows[self.sel]
        top_y = row.winfo_y()
        height = row.winfo_height()
        total = max(1, self.inner.winfo_height())
        view = self.canvas.winfo_height()
        if total <= view:
            return
        cur = self.canvas.yview()[0] * total
        if top_y < cur:
            self.canvas.yview_moveto(top_y / total)
        elif top_y + height > cur + view:
            self.canvas.yview_moveto((top_y + height - view) / total)

    def wheel(self, direction):
        if self.canvas is not None:
            self.canvas.yview_scroll(direction * 3, "units")

    # -------------------------------------------------------------- klavye
    def on_up(self, _):
        if self.rows and not self.busy:
            self.sel = (self.sel - 1) % len(self.rows)
            self.paint()

    def on_down(self, _):
        if self.rows and not self.busy:
            self.sel = (self.sel + 1) % len(self.rows)
            self.paint()

    def on_enter(self, _):
        if self.rows and not self.busy:
            self.rows[self.sel].event_generate("<Button-1>")

    def on_escape(self, _):
        if self.busy:
            return
        if self.back_cb:
            self.back_cb()
        else:
            self.quit_app()

    # -------------------------------------------------------------- ekranlar
    def screen_main(self):
        self.menu(C.t("title"), C.t("subtitle"), [
            (C.t("troubleshoot"), self.screen_troubleshoot),
            (C.t("reboot"), self.do_reboot),
            (C.t("cont_exit"), self.quit_app),
        ], back=None, size=48)

    def screen_troubleshoot(self):
        self.menu(C.t("troubleshoot"), C.t("select_cat"), [
            (C.t("auto") + "  —  " + C.t("auto_desc"), self.do_auto),
            (C.t("advanced"), self.screen_advanced),
            (C.t("view_log"), self.screen_log),
            ("← " + C.t("back"), self.screen_main),
        ], back=self.screen_main)

    def screen_advanced(self):
        items = [("%s   %s" % (c["icon"], C.cname(c)),
                  (lambda k=c["key"]: self.screen_category(k))) for c in C.CATALOG]
        items.append(("> " + C.t("terminal"), self.open_terminal))
        items.append(("← " + C.t("back"), self.screen_troubleshoot))
        self.menu(C.t("advanced"), C.t("select_cat"), items,
                  back=self.screen_troubleshoot, size=34)

    def screen_category(self, key):
        cat = C.by_key(key)
        items = []
        for act in cat["actions"]:
            items.append(("%s   [%s]" % (C.adesc(act), C.risk_label(act)),
                          (lambda a=act, c=cat: self.do_single(c, a))))
        items.append((C.t("run_cat"), (lambda c=cat: self.do_batch(
            [(c, a) for a in C.safe_actions(c)], C.cname(c)))))
        items.append(("← " + C.t("back"), self.screen_advanced))
        self.menu(C.cname(cat), C.cdesc(cat), items,
                  back=self.screen_advanced, size=30)

    def screen_log(self):
        self.clear()
        self.busy = False
        self.back_cb = self.screen_troubleshoot
        self.title(C.t("view_log"), C.LOG_FILE, 30)
        box = tk.Frame(self.shell, bg=BG)
        box.pack(fill=tk.BOTH, expand=True)
        txt = tk.Text(box, font=("Consolas", 10), bg=DARK, fg=TEXT,
                      insertbackground=ACCENT, wrap=tk.NONE, bd=0)
        scr = tk.Scrollbar(box, command=txt.yview)
        txt.configure(yscrollcommand=scr.set)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(fill=tk.BOTH, expand=True)
        try:
            with open(C.LOG_FILE, "r", encoding="utf-8", errors="replace") as fh:
                body = "".join(fh.readlines()[-500:]) or C.t("log_empty")
        except OSError:
            body = C.t("log_empty")
        txt.insert("1.0", body)
        txt.configure(state=tk.DISABLED)
        txt.see(tk.END)
        row = tk.Label(self.shell, text="← " + C.t("back"), font=self.f(15),
                       bg=ACCENT, fg=DARK, padx=26, pady=12, cursor="hand2")
        row.pack(anchor="w", pady=14)
        row.bind("<Button-1>", lambda e: self.screen_troubleshoot())
        self.rows = [row]
        self.sel = 0
        self.footer()

    # ------------------------------------------------------------- calistirma
    def do_single(self, cat, act):
        if act["risk"] == "high":
            if not messagebox.askyesno(C.t("confirm"), "%s\n\n%s\n\n%s" %
                                       (C.t("high"), C.adesc(act), C.t("ask"))):
                return
        self.do_batch([(cat, act)], C.adesc(act))

    def do_auto(self):
        if not messagebox.askyesno(C.t("auto"), "%s\n\n%s" % (C.t("auto_desc"), C.t("ask"))):
            return
        self.do_batch(C.auto_actions(), C.t("auto"))

    def do_batch(self, pairs, title):
        self.clear()
        self.busy = True
        self.rows = []
        self.back_cb = None
        self.title("%s: %s" % (C.t("repairing"), title), C.t("wait"), 30)

        self.pct = tk.Label(self.shell, text="0 %", font=self.f(13, "bold"),
                            fg=ACCENT, bg=BG, anchor="w")
        self.pct.pack(fill=tk.X)
        self.bar = tk.Canvas(self.shell, height=22, bg=SOFT, highlightthickness=0, bd=0)
        self.bar.pack(fill=tk.X, pady=(6, 18))

        box = tk.Frame(self.shell, bg=BG)
        box.pack(fill=tk.BOTH, expand=True)
        self.out = tk.Text(box, font=("Consolas", 10), bg=DARK, fg=TEXT,
                           wrap=tk.WORD, bd=0, height=14)
        scr = tk.Scrollbar(box, command=self.out.yview)
        self.out.configure(yscrollcommand=scr.set)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        self.out.pack(fill=tk.BOTH, expand=True)
        self.footer(nav=False)

        threading.Thread(target=self._worker, args=(pairs, title), daemon=True).start()

    def _say(self, text):
        self.root.after(0, self._append, text)

    def _append(self, text):
        try:
            self.out.insert(tk.END, text + "\n")
            self.out.see(tk.END)
        except tk.TclError:
            pass

    def _progress(self, done, total, label):
        self.root.after(0, self._paint_bar, done, total, label)

    def _paint_bar(self, done, total, label):
        try:
            pct = int(done / max(1, total) * 100)
            self.pct.config(text="%d %%   —   %s" % (pct, label))
            self.bar.delete("all")
            width = max(1, self.bar.winfo_width())
            self.bar.create_rectangle(0, 0, width * pct / 100, 22, fill=ACCENT, outline="")
        except tk.TclError:
            pass

    def _worker(self, pairs, title):
        total = len(pairs)
        ok = skipped = 0
        C.log("BATCH START: %s (%d islem)" % (title, total))
        for idx, (cat, act) in enumerate(pairs, start=1):
            label = "%s > %s" % (C.cname(cat), C.adesc(act))
            self._progress(idx - 1, total, label)
            self._say("\n▶ [%d/%d] %s" % (idx, total, label))
            status, body = C.execute(act)
            if status == "ok":
                ok += 1
            elif status == "skip":
                skipped += 1
            self._say(body)
            self._say("[%s]" % C.t(status))
            C.log("%s -> %s" % (label, status), "INFO" if status == "ok" else "WARN")
            self._progress(idx, total, label)
        C.log("BATCH END: %s (%d/%d ok, %d skip)" % (title, ok, total, skipped))
        self.root.after(0, self._finish, title, ok, total, skipped)

    def _finish(self, title, ok, total, skipped):
        summary = "%s\n\n%s: %d/%d\n%s: %d\n\n%s: %s" % (
            title, C.t("success"), ok, total, C.t("skip"), skipped, C.t("details"), C.LOG_FILE)
        self.menu(C.t("done"), summary, [
            ("← " + C.t("back"), self.screen_advanced),
            (C.t("view_log"), self.screen_log),
            (C.t("reboot"), self.do_reboot),
            (C.t("exit"), self.quit_app),
        ], back=self.screen_advanced, size=38)
        messagebox.showinfo(C.t("done"), summary)

    # ------------------------------------------------------------- eylemler
    def open_terminal(self):
        for cmd in (["x-terminal-emulator"], ["gnome-terminal"], ["konsole"],
                    ["xfce4-terminal"], ["mate-terminal"], ["xterm"]):
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                C.log("Terminal acildi: %s" % cmd[0])
                return
            except (OSError, FileNotFoundError):
                continue
        messagebox.showerror(C.t("terminal"), C.t("term_fail"))

    def do_reboot(self):
        if messagebox.askyesno(C.t("reboot"), C.t("reboot_q")):
            C.log("Sistem yeniden baslatiliyor", "WARN")
            subprocess.Popen(["systemctl", "reboot"])

    def quit_app(self):
        if messagebox.askyesno(C.t("exit"), C.t("exit_q")):
            C.log("GUI kapatildi")
            self.root.destroy()


def main():
    if "--version" in sys.argv:
        print("%s %s - %s" % (C.APP_NAME, C.VERSION, C.COPYRIGHT))
        return 0
    if not C.is_root():
        print(C.t("root_needed"))
        return 1
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("DISPLAY yok. Terminal surumunu kullanin: parol")
        return 1
    root = tk.Tk()
    Recovery(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
