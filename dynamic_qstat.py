import argparse
import curses
import datetime
import subprocess
import time


months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
          "août", "septembre", "octobre", "novembre", "décembre"]
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi",
         "Vendredi", "Samedi", "Dimanche"]


class NotParsedError(Exception):
    # custom error
    pass


# curses window as context manager
class cursesinit:
    def __init__(self, *args, **kwargs):
        self._stdscr = curses.initscr(*args, **kwargs)
        self._stdscr.scrollok(True)

    def __enter__(self):
        return self._stdscr

    def __exit__(self, exc_type, exc_value, traceback):
        curses.endwin()


class DynamicQstat:
    def __init__(self, command, update_time):
        self.run(command, update_time)

    def get_text(self, command, update_time):
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE)
        proc.wait()
        text = proc.communicate()[0].decode("utf-8")
        del proc
        d = datetime.datetime.now()
        # add refresh rate
        info = "\nRefresh rate = %.1f seconds." % update_time
        # add exit information after text
        info += "\nType CTRL+c to exit.\n\n"
        # add time
        text = ("%s %i %s %i %s:%s:%s\n" %
                (jours[d.weekday()],
                 d.day,
                 months[d.month - 1],
                 d.year,
                 str(d.hour).zfill(2),
                 str(d.minute).zfill(2),
                 str(d.second).zfill(2))
                + info + text)
        # add username on top
        return " ".join(command) + '\n' + text

    def run(self, command, update_time):
        with cursesinit() as stdscr:
            try:
                while True:
                    text = self.get_text(command, update_time)
                    lines = text.split("\n")
                    if len(lines) > curses.LINES:
                        lines = lines[:curses.LINES]
                        text = "\n".join(lines)
                    stdscr.move(0, 0)
                    # print text
                    stdscr.addstr(text)
                    # refresh screen
                    stdscr.refresh()
                    # wait for user input
                    time.sleep(update_time)
            except KeyboardInterrupt:
                pass


class DynamicQstatArgParser:
    def __init__(self):
        self.parser = self.create_parser()
        self._username = None
        self._timer = None
        self._command = None

    @property
    def username(self):
        if self._username is None:
            raise NotParsedError("Parser not parsed.")
        return self._username

    @username.setter
    def username(self, value):
        if not isinstance(value, str):
            raise TypeError("username should be a string.")
        self._username = value

    @property
    def timer(self):
        if self._timer is None:
            raise NotParsedError("Parser not parsed.")
        return self._timer

    @timer.setter
    def timer(self, value):
        if not isinstance(value, int) and not isinstance(value, float):
            raise TypeError("Timer should be an int or a float.")
        self._timer = value

    @property
    def command(self):
        if self._command is None:
            raise NotParsedError("Parser not parsed.")
        return self._command

    @command.setter
    def command(self, value):
        if not isinstance(value, str):
            raise TypeError("Command should be a string.")
        self._command = self.generate_command(value)

    def parse_args(self):
        args = vars(self.parser.parse_args())
        self.username = args["username"]
        self.timer = args["timer"]
        self.command = args["command"]

    def generate_command(self, cmd_str):
        # from a command string, generate the command list for the subprocess
        return cmd_str.split()

    def get_final_command(self):
        if self.username == "" and self.command == "":
            raise ValueError("No username and no command to return.")
        if self.username == "":
            return self.command
        return ["qstat", "-u", self.username]

    def create_parser(self):
        parser = argparse.ArgumentParser(description="Affichage dynamique"
                                                     " d'une commande.")
        parser.add_argument("--username", "-u", type=str, default="",
                            help="The username to check the qstat.")
        parser.add_argument("--timer", "-t", type=float, default=5,
                            help="Time between the qstat calls in seconds.")
        parser.add_argument("--command", "-c", type=str, default="",
                            help="Another command to run instead of qstat."
                                 " If this is used, the -u arg will be"
                                 " dismissed.")
        return parser


if __name__ == "__main__":
    dp = DynamicQstatArgParser()
    dp.parse_args()
    DynamicQstat(dp.get_final_command(), dp.timer)
