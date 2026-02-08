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

argc = len(sys.argv)
argv = sys.argv[1:]
join_part = True
purge_bots = False
bots = []
botfile = "botfile.txt"

def load_botfile(bfile):
    botfile_bots = []
    with open(bfile, "r") as bot_file:
        for nick in bot_file:
            botfile_bots.append(nick.strip("\n"))
    return botfile_bots

def clean_logs(logfile):
    filename = logfile.split(".")[0]
    tmpfile = f"{filename}.tmp"
    with open(logfile, 'r') as infile, \
        open(tmpfile, 'w') as outfile:

        for line in infile:
            stripped = line.strip("\n")
            split = stripped.split()
            if join_part == True and split[1] == "***":
                pass
            elif purge_bots == True and split[1].strip("<>") in bots:
                pass
            else:
                outfile.write(line)

if __name__ == "__main__":
    if argc <= 1:
        print("Usage: logclean <filename>.log")
        sys.exit(1)
    '''
    if '-b' in argv:
        purge_bots = True
        bots = load_botfile(botfile)
    '''
    clean_logs("2026-01-01.log") # <--- FIX THIS
    sys.exit(0)