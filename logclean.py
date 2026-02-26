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


# TODO


from math import log
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


def load_botfile(bfile):
    botfile_bots = []
    botfile = pathlib.Path(bfile)
    with botfile.open("r", encoding="utf-8", errors="replace") as bot_file:
        for nick in bot_file:
            botfile_bots.append(nick.rstrip("\n"))
    return botfile_bots


def load_logfiles(logpath):
    logfiles = []
    logs = pathlib.Path(logpath).glob("*.log")
    for file in logs:
        logfiles.append(file)
    return logfiles


def should_purge(line, join_part, purge_bots, bots):
    split = line.split()
    purge = False

    if not split:
        return False
    if join_part and len(split) > 2 and split[1] == "***":
        if split[2] in ["Joins:", "Parts:", "Quits:"]:
            purge = True
    if purge_bots and len(split) > 1 and split[1].strip("<>") in bots:
        purge = True

    return purge


def stdin_parse(stream, join_part, purge_bots, bots):
    purge = should_purge(stream, join_part, purge_bots, bots)
    if not purge:
        try:
            print(stream)
        except BrokenPipeError:
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)


def parse_logs(logfile, join_part, purge_bots, bots, replace_logs, dry_run, quiet):
    logfile = pathlib.Path(logfile)
    tmpfile = logfile.with_name(f"{logfile.name}.tmp")
    original_filesize = logfile.stat().st_size
    lines_removed = 0
    with logfile.open('r', encoding='utf-8', errors='replace') as infile, \
        tmpfile.open('w', encoding='utf-8', errors='replace') as outfile:
        
        for line in infile:
            purge = should_purge(line, join_part, purge_bots, bots)
            if purge:
                lines_removed += 1
            else:
                outfile.write(line)

    cleaned_filesize = tmpfile.stat().st_size
    space_savings = round((original_filesize - cleaned_filesize) / 1048576, 2)
    print_out(f"{logfile.resolve()} cleaned. {space_savings}mb saved.", quiet)
    if replace_logs:
        tmpfile.replace(logfile)
    elif dry_run:
        tmpfile.unlink()
    return space_savings, lines_removed


def logclean_interactive(logfiles, join_part, purge_bots, bots, replace_logs, dry_run, quiet):
    space_saved = 0
    lines_purged = 0
    timestamp = datetime.now().strftime("%Y-%m-%d [%H:%M:%S]")
    print_out(f"{timestamp} Cleaning...", quiet)
    start_time = monotonic()
    sorted_logfiles = sorted(logfiles)
    for logfile in sorted_logfiles:
        try:
            savings, lines_removed = parse_logs(logfile, join_part, purge_bots, bots, replace_logs, dry_run, quiet)
            space_saved += savings
            lines_purged += lines_removed
        except FileNotFoundError:
            print_out(f"{logfile}: file not found, skipping.", quiet)
    end_time = monotonic()
    elapsed = round(end_time - start_time, 3)
    print_out(f"Cleaning duration: {elapsed} seconds.", quiet)
    savings_rounded = round(space_saved, 2)
    if replace_logs:
        print_out(f"Lines purged: {lines_purged}\nTotal recovery: {savings_rounded}mb.", quiet)
    elif dry_run:
        print_out(f"{lines_purged} lines would be purged.\nCleaned files would be {savings_rounded}mb smaller.", quiet)
    else:
        print_out(f"Lines purged: {lines_purged}\nCleaned files are {savings_rounded}mb smaller.", quiet)


def logclean_log(data):
    try:
        with LOGCLEAN_FILE.open("a", encoding="utf-8", errors="replace") as logging:
            logging.write(f"{data}\n")
    except Exception:
        print("Couldn't open logclean log file.")


def print_out(data, quiet):
    if quiet and LOGGING:
        logclean_log(data)
    elif not quiet:
        print(data)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Clean IRC/ZNC logs.")
    p.add_argument("path", nargs="?", help="Log file or directory to clean")
    p.add_argument("-b", "--botfile", nargs="?", help="File containing bot nicks, one per line")
    p.add_argument("-j", "--join-part", action="store_true",
                   help="Remove JOIN/PART/QUIT lines")
    p.add_argument("-n", "--dry-run", action="store_true",
                   help="Don't modify files, just report")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress per-file summary output")
    p.add_argument("-r", "--replace", action="store_true",
                   help="Replace original file with cleaned version")
    p.add_argument("-y", "--no-auth", action="store_true",
                   help="Proceed without confirmation")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    join_part = args.join_part
    noauth_clean = args.no_auth
    replace_logs = args.replace
    purge_bots = False
    dir_clean = False
    file_clean = False
    dry_run = args.dry_run
    quiet = args.quiet
    stdin = not sys.stdin.isatty()
    logfiles = None if stdin else []
    bots = set()

    if not stdin and args.path is None:
        print("No input provided. Specify a log file/directory or provide input via stdin.")
        sys.exit(1)
    if args.botfile:
        purge_bots = True
        bots = set(load_botfile(args.botfile))
    if args.botfile is None and '-b' or '--botfile' in sys.argv:
        purge_bots = True
        bots = set(load_botfile(LOGCLEAN_BOTFILE))
    if not stdin:
        logfiles = load_logfiles(args.path)
        dir_clean = pathlib.Path(args.path).is_dir()
        file_clean = pathlib.Path(args.path).is_file()
        if file_clean:
            logfiles.append(pathlib.Path(args.path)) # type: ignore
    if not logfiles and not stdin:
        print("No log files found to clean. Exiting.")
        sys.exit(2)
    elif dir_clean and file_clean:
        print("Conflicting flags: -l and -d; Exiting.")
        sys.exit(1)
    elif replace_logs and dry_run:
        print("Conflicting flags: -r and -t; Exiting.")
        sys.exit(1)
    elif stdin:
        for line in sys.stdin:
            stdin_parse(line.rstrip("\n"), join_part, purge_bots, bots)
        sys.exit(0)
    else:
        if not purge_bots and not join_part:
            print("No flags provided, nothing to clean.")
            sys.exit(1)
        elif purge_bots and not join_part:
            print_out("Purging bots.", quiet)
        elif join_part and not purge_bots:
            print_out("Purging join/part messages.", quiet)
        elif purge_bots and join_part:
            print_out("Purging bots and join/part messages.", quiet)
        if not noauth_clean:
            confirm = input("Are you sure you want to clean logs? (y/n): ")
            if confirm.lower() != "y":
                print("Aborting.")
                sys.exit(1)
        else:
            print_out("Proceeding without confirmation.", quiet)

        logclean_interactive(logfiles, join_part, purge_bots, bots, replace_logs, dry_run, quiet)

    sys.exit(0)


if __name__ == "__main__":
    main()
