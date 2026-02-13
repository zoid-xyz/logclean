# logclean -- an IRC/ZNC Log Cleaning Utility

## Table of Contents
- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Botfile Format](#botfile-format)
- [Notes](#notes)
- [Todo](#notes)
- [License](#license)

## About

`logclean` is a lightweight utility designed for cleaning high-volume IRC or ZNC logs.

Many IRC channels include:

- Bots  
- ASCII art  
- Frequent JOIN/PART/QUIT events  
- Noise unrelated to actual conversation  

I like keeping long-term logs, but the clutter makes them huge fast.  
`logclean` solves that by allowing you to:

- Purge any nick listed in a botfile (e.g., bots, script users, spam)
- Remove JOIN/PART lines
- Clean individual logs or entire directories
- Optionally replace the originals with cleaned versions

It assumes traditional ZNC log formatting such as:
  
[HH:MM:SS] &lt;alcamus&gt; message  
[HH:MM:SS] *** Joins: alcamus (~alcamus@user/alcamus) alcamus

## Installation

1. Clone the [SourceHut](https://git.sr.ht/~zoid/logclean-python) repository:

```bash
git clone https://git.sr.ht/~zoid/logclean-python
chmod +x logclean.py
sudo mv logclean.py /usr/local/bin/logclean
```

or  

1. Clone the [Github](https://github.com/zoid-xyz/logclean.git) repository:
```bash
git clone https://github.com/zoid-xyz/logclean.git
chmod +x logclean.py
sudo mv logclean.py /usr/local/bin/logclean
```

## Usage
To run the project, use the following command:
```bash
logclean [options]

Flags:
-b <botfile> : Purge bot messages based on botfile
-d <dir>     : Clean all logs in the provided directory
-j           : Remove join/part messages
-l <logfile> : Specify a single log file to clean
-q           : Quiet; does not print output to terminal
-r           : Removes original logs, replaces with cleaned logs
-t           : Testing (dry run), displays would-be savings
-y           : Proceed without confirmation (use with caution)
-h           : Display this help message
```

## Examples
Remove join/part messages from a single log:
```bash
logclean -l #channel.log -j
```
Purge bots from a custom bot file:
```bash
logclean -l #channel.log -b botfile.txt
```
Clean an entire directory, purge bots, remove events, and overwrite originals:
```bash
logclean -d /var/znc/users/myuser/moddata/log/ -b botfile.txt -j -r
```

## Botfile Format
Botfiles contain **one** nick per line, exactly as it appears in logs:
```
ChanServ
NickServ
ASCIIBot
WeatherScript
```

## Notes
-d and -l cannot be used together.
  
-j and/or -b must be provided; otherwise nothing is cleaned.
  
Without -r, cleaned logs are written to .tmp files.
  
The script is designed for ZNC logs but works with any compatible format.
  
`logclean` only parses files and cleans files ending in *.log
  
This script removes only join/part/quit messages with the -j flag. Other
channel events are preserved.
  
Default behavior when -q is provided will be to log output to ~/.logclean/logclean.log
This behavior can be prevented by editing the LOGGING boolean at the top of the script.
  
The script was written with speed and memory in mind, no regex, 
only strip() and simple comparisons.

## Todo
  
Began using pathlib for logclean logging, implement pathlib everywhere applicable.
  
Implement STDIN/STDOUT to support UNIX pipes in both directions. (for a future project in mind)
  
Add to the logclean stats already implemented, removed/kept lines, etc.
  
Implement a dry run feature, allow user to test script on logs without modifying them
so the user can see what space will be saved on their system.
  
## License
This project is licensed under the [2-Clause BSD license](LICENSE).
