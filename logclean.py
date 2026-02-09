#!/usr/bin/python3

# TODO
# !!! Directory search is broken-ish, it only looks for .log files in the provided directory, not subdirectories.
# !!! Among other issues.
# !!! Botfile will only load if it's in the same directory as the script.
# Add computation time display (how long did this take to clean?)
# Add disk savings display (how much disk space have I saved?)

import os
import sys
import getopt

def load_botfile(bfile):
    botfile_bots = []
    with open(bfile, "r", encoding='utf-8', errors='replace') as bot_file:
        for nick in bot_file:
            botfile_bots.append(nick.strip("\n"))
    return botfile_bots

def load_logfiles(logpath):
    logfiles = []
    for file in os.listdir(logpath):
        if file.endswith(".log"):
            logfiles.append(f"{logpath}/{file}")
    return logfiles

def clean_logs(logfile, join_part, purge_bots, bots, replace_logs):
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
    if replace_logs:
        os.replace(tmpfile, logfile)

def main():
    argc = len(sys.argv)
    argv = sys.argv[1:]
    join_part = None
    purge_bots = None
    noauth_clean = None
    replace_logs = None
    bots = []
    botfile = "botfile.txt"
    logfiles = []

    if argc <= 1:
        print("Usage: logclean <filename>.log [options -c -b -j -h -y -l -r]")
        sys.exit(1)
    try:
        opts, args = getopt.getopt(argv, "c:brjhyl:")

        for opt, val in opts:
            match opt:
                case "-c":
                    logfiles = load_logfiles(val)
                
                case "-b":
                    purge_bots = True
                    if val:
                        botfile = val
                    try:
                        bots = load_botfile(botfile)
                    except FileNotFoundError:
                        print(f"Botfile {botfile} not found. Exiting.")
                        sys.exit(65)
                
                case "-j":
                    join_part = True
                
                case "-l":
                    logfiles.append(val)
                
                case "-r":
                    replace_logs = True
                
                case "-y":
                    noauth_clean = True
                
                case "-h":
                    print("Usage: logclean <filename>.log [options -c -b -j -h]")
                    print("Flags:")
                    print("-c           : Clean all logs in the provided directory")
                    print("-b <botfile> : Purge bot messages based on botfile")
                    print("-j           : Remove JOIN/PART messages")
                    print("-l <logfile> : Specify a single log file to clean")
                    print("-r           : Removes original logs, replaces with cleaned logs.")
                    print("-y           : Proceed without confirmation (use with caution)")
                    print("-h           : Display this help message")
                    sys.exit(0)

    except getopt.GetoptError as err:
        print(err)
        print("Usage: logclean <filename>.log [options -c -b -j -h]")
        sys.exit(2)

    if not logfiles:
        print("No log files found to clean. Exiting.")
        sys.exit(1)
    else:
        if not purge_bots and not join_part:
            print("No flags provided, nothing to clean.")
            sys.exit(1)
        elif purge_bots and not join_part:
            print("Purging bots.")
        elif join_part and not purge_bots:
            print("Purging JOIN/PART messages.")
        elif purge_bots and join_part:
            print("Purging bots and JOIN/PART messages.")
        if not noauth_clean:
            confirm = input(f"Are you sure you want to clean logs? (y/n): ")
            if confirm.lower() != 'y':
                print("Aborting.")
                sys.exit(1)
        else:
            print("Proceeding without confirmation.")
        print("Cleaning...")
        for logfile in logfiles:
            clean_logs(logfile, join_part, purge_bots, bots, replace_logs)
    sys.exit(0)

if __name__ == "__main__":
    main()
