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
# Add computation time display (how long did this take to clean?)
# Add disk savings display (how much disk space have I saved?)

import os
import sys
import getopt

def load_botfile(bfile):
    botfile = os.path.abspath(bfile)
    botfile_bots = []
    with open(botfile, "r", encoding='utf-8', errors='replace') as bot_file:
        for nick in bot_file:
            botfile_bots.append(nick.rstrip("\n"))
    return botfile_bots

def load_logfiles(logpath):
    logfiles = []
    for file in os.listdir(logpath):
        if file.endswith(".log"):
            logfiles.append(os.path.join(logpath, file))
    return logfiles

def clean_logs(logfile, join_part, purge_bots, bots, replace_logs, quiet):
    filename, _ = os.path.splitext(logfile)
    tmpfile = f"{filename}.tmp"
    original_filesize = os.path.getsize(logfile)
    with open(logfile, 'r', encoding='utf-8', errors='replace') as infile, \
        open(tmpfile, 'w', encoding='utf-8', errors='replace') as outfile:

        for line in infile:
            stripped = line.rstrip("\n")
            split = stripped.split()
            if not split:
                continue
            if join_part and len(split) > 1 and split[1] == "***":
                if split[2] in ['Joins:', 'Parts:', 'Quits:']:
                    continue
            if purge_bots and len(split) > 1 and split[1].strip("<>") in bots:
                continue
            outfile.write(line)
        
    cleaned_filesize = os.path.getsize(tmpfile)
    space_savings = round((original_filesize - cleaned_filesize) / 1048576, 2)
    print_out(f"{logfile} cleaned. {space_savings}mb saved.", quiet)
    if replace_logs:
        os.replace(tmpfile, logfile)
    return space_savings

def print_out(data, quiet):
    if not quiet:
        print(data)

def main():
    argc = len(sys.argv)
    argv = sys.argv[1:]
    join_part = None
    purge_bots = None
    noauth_clean = None
    replace_logs = None
    dir_clean = None
    file_clean = None
    quiet = None
    space_saved = 0
    bots = []
    botfile = "botfile.txt"
    logfiles = []
    usage = "Usage: logclean [options -d -b -j -h -y -l -r -q]"

    if argc <= 1:
        print(usage)
        sys.exit(1)
    try:
        opts, args = getopt.getopt(argv, "d:b:l:rjhqy")

        for opt, val in opts:
            match opt:
                case "-d":
                    dir_clean = True
                    try:
                        logfiles = load_logfiles(val)
                    except FileNotFoundError:
                        print(f"Directory {val} not found. Exiting.")
                        sys.exit(65)
                
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
                    file_clean = True
                    logfiles.append(val)
                
                case "-r":
                    replace_logs = True
                
                case "-y":
                    noauth_clean = True
                
                case "-q":
                    quiet = True
                
                case "-h":
                    print(usage)
                    print("Flags:")
                    print("-d <dir>     : Clean all logs in the provided directory")
                    print("-b <botfile> : Purge bot messages based on botfile")
                    print("-j           : Remove join/part messages")
                    print("-l <logfile> : Specify a single log file to clean")
                    print("-r           : Removes original logs replaces with cleaned logs")
                    print("-q           : Quiet; does not print output to terminal")
                    print("-y           : Proceed without confirmation (use with caution)")
                    print("-h           : Display this help message")
                    sys.exit(0)

    except getopt.GetoptError as err:
        print(err)
        print(usage)
        sys.exit(2)

    if not logfiles:
        print("No log files found to clean. Exiting.")
        sys.exit(65)
    elif dir_clean and file_clean:
        print("Conflicting flags: -l and -d; Exiting.")
        sys.exit(1)
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
            confirm = input(f"Are you sure you want to clean logs? (y/n): ")
            if confirm.lower() != 'y':
                print("Aborting.")
                sys.exit(1)
        else:
            print_out("Proceeding without confirmation.", quiet)
        print_out("Cleaning...", quiet)
        sorted_logfiles = sorted(logfiles)
        for logfile in sorted_logfiles:
            try:
                savings = clean_logs(logfile, join_part, purge_bots, bots, replace_logs, quiet)
                space_saved = space_saved + savings
            except FileNotFoundError:
                print(f"{logfile}: file not found, skipping.")
    savings_rounded = round(space_saved, 2)
    print_out(f"Total recovery: {savings_rounded}mb.", quiet)
    sys.exit(0)

if __name__ == "__main__":
    main()
