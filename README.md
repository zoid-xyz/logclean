## Table of Contents
- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## About
I am writing this because I am in a lot of high volume IRC channels,
many of which have bots and plenty of ASCII art. I enjoy keeping my 
logs long term, but due to the volume of ASCII art the logs get quite
large. By putting the bots into a botfile.txt and loading it I can
purge all bots and ASCII art. This script also allows me to purge
all JOINS/PARTS as those are also unnecessary for my uses.

## Installation
1. Clone the repository:
```bash
 git clone https://git.sr.ht/~zoid/logclean-python
```

2. Install dependencies:
```bash
 chmod +x logclean.py && sudo mv /usr/local/bin/logclean
```
## Usage
To run the project, use the following command:
```bash
logclean [options]
```

## License
This project is licensed under the [2-Clause BSD license](LICENSE).
