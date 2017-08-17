import curses
import subprocess
import time
import datetime

stdscr = curses.initscr()
months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

try:
    (h, w) = stdscr.getmaxyx()
    while True:
        proc = subprocess.Popen(["qstat", "-u", "fgoudrea"], stdout=subprocess.PIPE)
        proc.wait()
        text = proc.communicate()[0].decode("utf-8")
        del proc
        stdscr.move(0, 0)
        d = datetime.datetime.now()
        text = "%s %i %s %i %i:%i:%i\n\n" % (jours[d.weekday()], d.day, months[d.month], d.year, d.hour, d.minute, d.second) + text
        stdscr.addstr(text)
        stdscr.refresh()
        time.sleep(5)
except KeyboardInterrupt:
    pass
finally:
    curses.endwin()
