import argparse
import curses
import datetime
import subprocess
import time


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


class DynamicQstat:
    def __init__(self, username, update_time):
        self.run(username, update_time)

    def run(self, username, update_time):
        with cursesinit() as stdscr:
            try:
                while True:
                    proc = subprocess.Popen(["qstat", "-u", username],
                                            stdout=subprocess.PIPE)
                    proc.wait()
                    text = proc.communicate()[0].decode("utf-8")
                    del proc
                    stdscr.move(0, 0)
                    d = datetime.datetime.now()
                    # add refresh rate
                    text += "\n\nRefresh rate = %.1f seconds." % update_time
                    # add exit information after text
                    text += "\nType CTRL+c to exit."
                    # add time
                    text = ("%s %i %s %i %s:%s:%s\n\n" % (jours[d.weekday()],
                                                          d.day,
                                                          months[d.month - 1],
                                                          d.year,
                                                          str(d.hour).zfill(2),
                                                          str(d.minute).zfill(2),
                                                          str(d.second).zfill(2))
                            + text)
                    # add username on top
                    text = "qstat -u %s\n" % username + text
                    stdscr.addstr(text)
                    stdscr.refresh()
                    time.sleep(update_time)
            except KeyboardInterrupt:
                pass


class DynamicQstatArgParser:
    def __init__(self):
        self.parser = self.create_parser()

    def parse_args(self):
        args = vars(self.parser.parse_args())
        self.username = args["username"]
        self.timer = args["timer"]

    def create_parser(self):
        parser = argparse.ArgumentParser(description="Affichage dynamique d'un"
                                                     " qstat pour un user.")
        parser.add_argument("username", type=str,
                            help="The username to check the qstat.")
        parser.add_argument("--timer", "-t", type=float, default=5,
                            help="Time between the qstat calls in seconds.")
        return parser


if __name__ == "__main__":
    dp = DynamicQstatArgParser()
    dp.parse_args()
    DynamicQstat(dp.username, dp.timer)
