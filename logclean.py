#!/usr/bin/python3

# TODO
# Allow user to provide .log from the terminal
# Allow user to provide flag to clean all logs in provided directory
# Fix case matching for flags
# Add removal of original and renaming of tmp file after cleaning.
# Add computation time display (how long did this take to clean?)
# Add disk savings display (how much disk space have I saved?)

import sys
import getopt

def load_botfile(bfile):
    botfile_bots = []
    with open(bfile, "r", encoding='utf-8', errors='replace') as bot_file:
        for nick in bot_file:
            botfile_bots.append(nick.strip("\n"))
    return botfile_bots

def clean_logs(logfile, join_part, purge_bots, bots):
    filename = logfile.split(".")[0]
    tmpfile = f"{filename}.tmp"
    with open(logfile, 'r', encoding='utf-8', errors='replace') as infile, \
        open(tmpfile, 'w', encoding='utf-8', errors='replace') as outfile:

        for line in infile:
            stripped = line.rstrip("\n")
            split = stripped.split()
            if not split:
                continue
            if join_part and len(split) > 1 and split[1] == "***":
                continue
            if purge_bots and len(split) > 1 and split[1].strip("<>") in bots:
                continue
            outfile.write(line)
    print(f"Finished cleaning {logfile}")

def main():
    argc = len(sys.argv)
    argv = sys.argv[1:]
    join_part = True
    purge_bots = True
    bots = []
    botfile = "botfile.txt"
    logfiles = ['2026-01-01.log']

    for logfile in logfiles:
        print(f"Cleaning {logfile}...")
        bots = load_botfile(botfile)
        clean_logs(logfile, join_part, purge_bots, bots)
    sys.exit(0)

# Replace the block below with getopt.
"""
    if argc <= 1:
        print("Usage: logclean <filename>.log")
        sys.exit(1)
    for arg in argv:
        if '-c' not in argv:
            if arg.endswith(".log"):
                logfiles.append(arg)
        elif '-c' in argv:
            pass
            #load files from directory
        elif '-b' in argv:
            purge_bots = True
            try:
                if arg.endswith(".txt"):
                    bots = load_botfile(arg)
                else:
                    bots = load_botfile(botfile)
            except FileNotFoundError:
                print(f"Botfile {botfile} not found. Please provide a valid botfile or ensure {botfile} exists.")
                sys.exit(1)
        elif '-j' in argv:
            join_part = True
        elif '-h' in argv:
            print("Usage: logclean <filename>.log")
            print("Flags:")
            print("-c : Clean all logs in the provided directory")
            print("-b : Purge lines from bots listed in botfile.txt")
            print("-j: Purge join/part messages")
            print("-h : Display this help message")
            sys.exit(0)
"""

if __name__ == "__main__":
    main()
