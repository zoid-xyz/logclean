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
    print(f"{logfile} cleaned.")

def main():
    argc = len(sys.argv)
    argv = sys.argv[1:]
    join_part = None
    purge_bots = None
    noauth_clean = None
    bots = []
    botfile = "botfile.txt"
    logfiles = ['2026-01-01.log']

    if argc <= 1:
        print("Usage: logclean <filename>.log [options -c -b -j -h]")
        sys.exit(1)
    try:
        opts, args = getopt.getopt(argv, "cbjhy")

        for opt, val in opts:
            if opt == "-c":
                print("Clean all logs in the provided directory flag set.")
                # TODO: load files from directory instead of args
            elif opt == "-b":
                purge_bots = True
                if val:
                    botfile = val
                try:
                    bots = load_botfile(botfile)
                except FileNotFoundError:
                    print(f"Botfile {botfile} not found. Exiting.")
                    sys.exit(65)
            elif opt == "-j":
                join_part = True
            elif opt == "-y":
                noauth_clean = True
            elif opt == "-h":
                print("Usage: logclean <filename>.log [options -c -b -j -h]")
                print("Flags:")
                print("-c           : Clean all logs in the provided directory")
                print("-b <botfile> : Purge bot messages based on botfile")
                print("-j           : Remove JOIN/PART messages")
                print("-y           : Proceed without confirmation (use with caution)")
                print("-h           : Display this help message")
                sys.exit(0)

    except getopt.GetoptError as err:
        print(err)
        print("Usage: logclean <filename>.log [options -c -b -j -h]")
        sys.exit(2)     
    for logfile in logfiles:
        if not purge_bots and not join_part:
            print("No flags provided, nothing to clean.")
            sys.exit(0)
        elif purge_bots and not join_part:
            print("Purging bots.")
        elif join_part and not purge_bots:
            print("Purging JOIN/PART messages.")
        elif purge_bots and join_part:
            print("Purging bots and JOIN/PART messages.")
        if not noauth_clean:
            confirm = input(f"Are you sure you want to clean {logfile}? (y/n): ")
            if confirm.lower() != 'y':
                print("Aborting.")
                sys.exit(0)
        else:
            print("Proceeding without confirmation.")
        print("Cleaning...")
        clean_logs(logfile, join_part, purge_bots, bots)
    sys.exit(0)

if __name__ == "__main__":
    main()
