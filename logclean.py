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


import sys
import getopt
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


def main():
    argc = len(sys.argv)
    argv = sys.argv[1:]
    join_part = False
    purge_bots = False
    noauth_clean = False
    replace_logs = False
    dir_clean = False
    file_clean = False
    dry_run = False
    quiet = False
    stdin = not sys.stdin.isatty()
    logfiles = None if stdin else []
    bots = set()
    usage = "Usage: logclean [options -d -b -B -l -h -j -q -r -t -y]"

    if argc <= 1:
        print(usage)
        sys.exit(1)
    try:
        opts, _ = getopt.getopt(argv, "b:d:l:Bhjqrty")

        for opt, val in opts:
            match opt:
                case "-b":
                    purge_bots = True
                    botfile = val
                    try:
                        bots = set(load_botfile(botfile))
                    except FileNotFoundError:
                        print(f"Botfile {botfile} not found. Exiting.")
                        sys.exit(2)
                
                case "-B":
                    purge_bots = True
                    botfile = LOGCLEAN_BOTFILE
                    try:
                        bots = set(load_botfile(botfile))
                    except FileNotFoundError:
                        print(f"Botfile {botfile} not found. Exiting.")
                        sys.exit(2)

                case "-d":
                    if stdin:
                        print("Cannot use -d when reading from stdin.")
                        sys.exit(2)
                    else:
                        dir_clean = True
                        try:
                            logfiles = load_logfiles(val)
                        except FileNotFoundError:
                            print(f"Directory {val} not found. Exiting.")
                            sys.exit(2)

                case "-j":
                    join_part = True

                case "-l":
                    if stdin:
                        print("Cannot use -l when reading from stdin.")
                        sys.exit(2)
                    else:
                        file_clean = True
                        logfiles.append(pathlib.Path(val)) # type: ignore

                case "-r":
                    replace_logs = True

                case "-t":
                    dry_run = True

                case "-q":
                    quiet = True

                case "-y":
                    noauth_clean = True

                case "-h":
                    print(usage)
                    print("Flags:")
                    print("-b <botfile> : Purge bot messages based on botfile")
                    print("-B           : Loads bots from ~/.logclean/botfile.txt")
                    print("-d <dir>     : Clean all logs in the provided directory")
                    print("-j           : Remove join/part messages")
                    print("-l <logfile> : Specify a single log file to clean")
                    print("-q           : Quiet; does not print output to terminal")
                    print("-r           : Removes original logs replaces with cleaned logs")
                    print("-t           : Testing (dry run), displays would-be savings")
                    print("-y           : Proceed without confirmation (use with caution)")
                    print("-h           : Display this help message")
                    sys.exit(0)

    except getopt.GetoptError as err:
        print(err)
        print(usage)
        sys.exit(2)

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
