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
- Remove JOIN/PART and other ZNC event lines (`***`)
- Clean individual logs or entire directories
- Optionally replace the originals with cleaned versions

It assumes traditional ZNC log formatting such as:
  
[HH:MM:SS] &lt;usernick&gt; message  
[HH:MM:SS] *** Joins: usernick (~usernick@user/usernick) usernick

## Installation

1. Clone the repository:

```bash
git clone https://git.sr.ht/~zoid/logclean-python
chmod +x logclean.py
sudo mv logclean.py /usr/local/bin/logclean
```

## Usage
To run the project, use the following command:
```bash
logclean [options]

Flags:
-c <dir>     : Clean all logs in the provided directory
-b <botfile> : Purge bot messages based on botfile
-j           : Remove join/part messages
-l <logfile> : Specify a single log file to clean
-r           : Removes original logs, replaces with cleaned logs
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
logclean -c /var/znc/users/myuser/moddata/log/ -b botfile.txt -j -r
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
-c and -l cannot be used together.
  
-j and/or -b must be provided; otherwise nothing is cleaned.
  
Without -r, cleaned logs are written to .tmp files.
  
The script is designed for ZNC logs but works with any compatible format.

The script was written with speed and memory in mind, no regex, 
only strip() and simple comparisons.
  
This script removes only join/part/quit messages with the -j flag. Other
channel events are preserved.  

## Todo
Add computation time display (how long did this take to clean?)
  
Add disk savings display (how much disk space have I saved?)
  
Add -o &lt;output_dir&gt; option.

## License
This project is licensed under the [2-Clause BSD license](LICENSE).
