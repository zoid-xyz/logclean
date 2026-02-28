#!/usr/bin/env python3

# Copyright (c) 2026, zoid <zoid.xyz@pm.me>
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import sys
import argparse
import pathlib
from time import monotonic
from datetime import datetime


LOGGING = True
LOGCLEAN_DIR = pathlib.Path.home() / ".logclean"
LOGCLEAN_FILE = LOGCLEAN_DIR / "logclean.log"
LOGCLEAN_BOTFILE = LOGCLEAN_DIR / "botfile.txt"
LOGCLEAN_DIR.mkdir(exist_ok=True)


class LogCleaner:

    def __init__(self, args):
        self.path = args.path
        self.join_part = args.join_part
        self.noauth_clean = args.no_auth
        self.replace_logs = args.replace
        self.purge_bots = False
        self.dry_run = args.dry_run
        self.quiet = args.quiet
        self.stdin = not sys.stdin.isatty()
        self.logfiles = None if self.stdin else []
        self.bots = set()
        if args.botfile:
            self.purge_bots = True
            self.load_botfile(args.botfile)
        if not args.botfile:
            if '-b' in sys.argv or '--botfile' in sys.argv:
                self.purge_bots = True
                self.load_botfile(LOGCLEAN_BOTFILE)


    def load_botfile(self, bfile):
        botfile_bots = []
        botfile = pathlib.Path(bfile)
        if botfile.exists():
            with botfile.open("r", encoding="utf-8", errors="replace") as bot_file:
                for nick in bot_file:
                    botfile_bots.append(nick.rstrip("\n"))
        else:
            print(f"Botfile {bfile} not found. Exiting.")
            sys.exit(1)
        self.bots = set(botfile_bots)


    def load_logfiles(self):
        base = pathlib.Path(self.path)
        logfiles = []

        if not base.exists() or not base.is_dir():
            self.logfiles = []
            return

        for path in base.rglob("*.log"):
            if path.is_file():
                logfiles.append(path)

        self.logfiles = sorted(logfiles)


    def should_purge(self, line):
        split = line.split()
        purge = False

        if not split:
            return False
        if self.join_part and len(split) > 2 and split[1] == "***":
            if split[2] in ["Joins:", "Parts:", "Quits:"]:
                purge = True
        if self.purge_bots and len(split) > 1 and split[1].strip("<>") in self.bots:
            purge = True
        
        return purge


    def stdin_parse(self, stream):
        purge = self.should_purge(stream)
        if not purge:
            try:
                print(stream)
            except BrokenPipeError:
                sys.exit(1)
            except KeyboardInterrupt:
                sys.exit(1)


    def parse_logs(self, logfile):
        logfile = pathlib.Path(logfile)
        tmpfile = logfile.with_name(f"{logfile.name}.tmp")
        original_filesize = logfile.stat().st_size
        lines_removed = 0
        with logfile.open('r', encoding='utf-8', errors='replace') as infile, \
            tmpfile.open('w', encoding='utf-8', errors='replace') as outfile:
        
            for line in infile:
                purge = self.should_purge(line)
                if purge:
                    lines_removed += 1
                else:
                    outfile.write(line)

        cleaned_filesize = tmpfile.stat().st_size
        space_savings = round((original_filesize - cleaned_filesize) / 1048576, 2)
        self.print_out(f"{logfile.resolve()} cleaned. {space_savings}mb saved.")
        if self.replace_logs:
            tmpfile.replace(logfile)
        elif self.dry_run:
            tmpfile.unlink()
        return space_savings, lines_removed


    def logclean_log(self, data):
        try:
            with LOGCLEAN_FILE.open("a", encoding="utf-8", errors="replace") as logging:
                logging.write(f"{data}\n")
        except Exception:
            print("Couldn't open logclean log file.")


    def print_out(self, data):
        if self.quiet and LOGGING:
            self.logclean_log(data)
        elif not self.quiet:
            print(data)


    def logclean_interactive(self):
        space_saved = 0
        lines_purged = 0
        timestamp = datetime.now().strftime("%Y-%m-%d [%H:%M:%S]")
        self.print_out(f"{timestamp} Cleaning...")
        start_time = monotonic()
        for logfile in self.logfiles: # type: ignore
            try:
                savings, lines_removed = self.parse_logs(logfile)
                space_saved += savings
                lines_purged += lines_removed
            except FileNotFoundError:
                self.print_out(f"{logfile}: file not found, skipping.")
        end_time = monotonic()
        elapsed = round(end_time - start_time, 3)
        self.print_out(f"Cleaning duration: {elapsed} seconds.")
        savings_rounded = round(space_saved, 2)
        if self.replace_logs:
            self.print_out(f"Lines purged: {lines_purged}\nTotal recovery: {savings_rounded}mb.")
        elif self.dry_run:
            self.print_out(f"{lines_purged} lines would be purged.\nCleaned files would be {savings_rounded}mb smaller.")
        else:
            self.print_out(f"Lines purged: {lines_purged}\nCleaned files are {savings_rounded}mb smaller.")


    def run(self):
        if not self.stdin and self.path is None:
            print("No input provided. Specify a log file/directory or provide input via stdin.")
            sys.exit(1)
        if not self.stdin:
            if pathlib.Path(self.path).is_dir():
                self.load_logfiles()
            if pathlib.Path(self.path).is_file():
                self.logfiles.append(pathlib.Path(self.path)) # type: ignore
        if self.replace_logs and self.dry_run:
            print("Conflicting flags: -r and -t; Exiting.")
            sys.exit(1)

        if self.stdin:
            for line in sys.stdin:
                self.stdin_parse(line.rstrip("\n"))
            sys.exit(0)
        else:
            if not self.purge_bots and not self.join_part:
                print("No flags provided, nothing to clean.")
                sys.exit(1)
            elif self.purge_bots and not self.join_part:
                self.print_out("Purging bots.")
            elif self.join_part and not self.purge_bots:
                self.print_out("Purging join/part messages.")
            elif self.purge_bots and self.join_part:
                self.print_out("Purging bots and join/part messages.")
            if not self.noauth_clean:
                confirm = input("Are you sure you want to clean logs? (y/n): ")
                if confirm.lower() != "y":
                    print("Aborting.")
                    sys.exit(1)
            else:
                self.print_out("Proceeding without confirmation.")

            self.logclean_interactive()
        
        sys.exit(0)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Clean IRC/ZNC logs.")
    p.add_argument("path", nargs="?", help="Log file or directory to clean")
    p.add_argument("-b", "--botfile", nargs="?", help="File containing bot nicks, one per line")
    p.add_argument("-j", "--join-part", action="store_true",
                   help="Remove JOIN/PART/QUIT lines")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress per-file summary output")
    p.add_argument("-r", "--replace", action="store_true",
                   help="Replace original file with cleaned version")
    p.add_argument("-t", "--dry-run", action="store_true",
                   help="Don't modify files, just report")
    p.add_argument("-y", "--no-auth", action="store_true",
                   help="Proceed without confirmation")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args(argv=None)
    cleaner = LogCleaner(args)
    cleaner.run()
