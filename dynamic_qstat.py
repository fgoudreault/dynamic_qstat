import curses
import subprocess
import time
import datetime
import sys


months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
          "août", "septembre", "octobre", "novembre", "décembre"]
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi",
         "Vendredi", "Samedi", "Dimanche"]


# curses window as context manager
class cursesinit:
    def __init__(self, *args, **kwargs):
        self._stdscr = curses.initscr(*args, **kwargs)

    def __enter__(self):
        return self._stdscr

    def __exit__(self, exc_type, exc_value, traceback):
        curses.endwin()


# parse the username
username = sys.argv[-1]
del sys.argv[-1]
if username == "dynamic_qstat.py":
    raise ValueError("Did not specify a username. SPECIFY ONE!")

with cursesinit() as stdscr:
    try:
        (h, w) = stdscr.getmaxyx()
        while True:
            proc = subprocess.Popen(["qstat", "-u", username],
                                    stdout=subprocess.PIPE)
            proc.wait()
            text = proc.communicate()[0].decode("utf-8")
            del proc
            stdscr.move(0, 0)
            d = datetime.datetime.now()
            # add exit information after text
            text += "\n\nType CTRL+c to exit."
            # add time
            text = ("%s %i %s %i %i:%i:%i\n\n" % (jours[d.weekday()], d.day,
                                                  months[d.month], d.year,
                                                  d.hour, d.minute, d.second)
                    + text)
            # add username on top
            text = "qstat -u %s\n" % username + text
            stdscr.addstr(text)
            stdscr.refresh()
            time.sleep(5)
    except KeyboardInterrupt:
        pass
